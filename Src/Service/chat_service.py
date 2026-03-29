"""
RAG chat service — Hybrid retrieval (Vector + BM25) + Cross-encoder re-ranking.
Uses versioned prompts from Src/Service/prompts/.
"""

from langchain_core.prompts import ChatPromptTemplate
from sqlalchemy.ext.asyncio import AsyncSession

from Src.Cache.cache import get_cached_response, set_cached_response
from Src.Config.config import get_settings
from Src.DTO.chat_dto import ChatResponse, CitationSchema
from Src.Error_Codes.exceptions import ErrorCode, NotFoundException
from Src.Loggers.logger import get_logger
from Src.Repository.conversation_repository import ConversationRepository
from Src.Repository.token_usage_repository import TokenUsageRepository
from Src.Repository.vector_repository import ChromaVectorRepository
from Src.Service.bedrock_factory import get_embedding_model, get_llm
from Src.Service.bm25_service import get_bm25_index
from Src.Service.prompts.prompt_registry import get_active_prompt
from Src.Service.reranker_service import rerank
from Src.Utilities.citation_utils import format_citations

logger = get_logger(__name__)
settings = get_settings()

VECTOR_K = 10  # fetch more candidates for hybrid merge
BM25_K = 10
RERANK_TOP_K = 5


def _build_prompt() -> ChatPromptTemplate:
    template = get_active_prompt()
    return ChatPromptTemplate.from_template(template)


class ChatService:
    def __init__(self, db: AsyncSession):
        self._vector_repo = ChromaVectorRepository(get_embedding_model())
        self._conv_repo = ConversationRepository(db)
        self._token_repo = TokenUsageRepository(db)
        self._llm = get_llm()

    async def chat(self, question: str, user_id: str, conversation_id: str | None) -> ChatResponse:
        # Cache check
        cached = get_cached_response(question, user_id)
        if cached and not conversation_id:
            logger.info("Cache hit")
            return ChatResponse(**cached)

        # ── Hybrid Retrieval ──
        vector_docs = await self._vector_repo.similarity_search(question, k=VECTOR_K)
        bm25_docs = get_bm25_index().search(question, k=BM25_K)

        # Merge & deduplicate by content
        seen, merged = set(), []
        for doc in vector_docs + bm25_docs:
            key = doc.page_content[:100]
            if key not in seen:
                seen.add(key)
                merged.append(doc)

        # ── Re-rank ──
        final_docs = rerank(question, merged, top_k=RERANK_TOP_K)
        context = "\n\n".join(d.page_content for d in final_docs)
        citations = [CitationSchema(**c) for c in format_citations(final_docs)]

        # ── Generate ──
        prompt = _build_prompt()
        chain = prompt | self._llm
        ai_message = await chain.ainvoke({"context": context, "question": question})
        answer = ai_message.content

        # ── Token usage ──
        usage = ai_message.response_metadata.get("usage", {})
        await self._token_repo.record(
            user_id=user_id,
            model_id=settings.bedrock_llm_model_id,
            model_type="llm",
            input_tokens=usage.get("prompt_tokens", usage.get("input_tokens", 0)),
            output_tokens=usage.get("completion_tokens", usage.get("output_tokens", 0)),
            conversation_id=conversation_id,
        )

        # ── Persist conversation ──
        if not conversation_id:
            conv = await self._conv_repo.create_conversation(user_id=user_id, title=question[:80])
            conversation_id = conv.id

        await self._conv_repo.add_message(conversation_id, "user", question)
        await self._conv_repo.add_message(
            conversation_id, "assistant", answer, sources=[c.model_dump() for c in citations]
        )

        response = ChatResponse(
            conversation_id=conversation_id,
            answer=answer,
            citations=citations,
        )
        set_cached_response(question, user_id, response.model_dump())
        return response

    async def get_history(self, conversation_id: str, user_id: str):
        conv = await self._conv_repo.get_by_id(conversation_id, user_id)
        if not conv:
            raise NotFoundException(ErrorCode.CONVERSATION_NOT_FOUND, "Conversation not found")
        return conv

    async def list_conversations(self, user_id: str):
        return await self._conv_repo.list_by_user(user_id)
