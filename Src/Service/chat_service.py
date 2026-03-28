"""
RAG chat service using LangChain LCEL pipeline.
Retrieves top-k chunks from ChromaDB, builds prompt, calls Claude Haiku.
"""
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from sqlalchemy.ext.asyncio import AsyncSession

from Src.Config.config import get_settings

from Src.Repository.vector_repository import ChromaVectorRepository
from Src.Repository.conversation_repository import ConversationRepository
from Src.Repository.token_usage_repository import TokenUsageRepository
from Src.Service.bedrock_factory import get_embedding_model, get_llm
from Src.Utilities.citation_utils import format_citations
from Src.Cache.cache import get_cached_response, set_cached_response
from Src.Error_Codes.exceptions import ChatException, ErrorCode, NotFoundException
from Src.DTO.chat_dto import ChatResponse
from Src.Loggers.logger import get_logger

logger = get_logger(__name__)

RAG_PROMPT = ChatPromptTemplate.from_template(
    """You are a helpful assistant. Answer the question using ONLY the context below.
If the answer is not in the context, say "I don't have enough information to answer that."

Context:
{context}

Question: {question}

Answer:"""
)

TOP_K = 5


class ChatService:
    def __init__(self, db: AsyncSession):
        self._vector_repo = ChromaVectorRepository(get_embedding_model())
        self._conv_repo = ConversationRepository(db)
        self._token_repo = TokenUsageRepository(db)
        self._llm = get_llm()
        self._chain = (
            {"context": RunnablePassthrough(), "question": RunnablePassthrough()}
            | RAG_PROMPT
            | self._llm
            | StrOutputParser()
        )

    async def chat(
        self, question: str, user_id: str, conversation_id: str | None
    ) -> ChatResponse:
        # Check cache first
        cached = get_cached_response(question, user_id)
        if cached and not conversation_id:
            logger.info("Cache hit for query")
            return ChatResponse(**cached)

        # Retrieve relevant chunks
        docs = await self._vector_repo.similarity_search(question, k=TOP_K)
        context = "\n\n".join(d.page_content for d in docs)
        citations = format_citations(docs)

        # Generate answer — use ainvoke with_config to get full AIMessage for token metadata
        settings = get_settings()
        llm_with_meta = RAG_PROMPT | self._llm
        ai_message = await llm_with_meta.ainvoke({"context": context, "question": question})
        answer = ai_message.content

        # Capture LLM token usage from response metadata
        usage = ai_message.response_metadata.get("usage", {})
        await self._token_repo.record(
            user_id=user_id,
            model_id=settings.bedrock_llm_model_id,
            model_type="llm",
            input_tokens=usage.get("prompt_tokens", usage.get("input_tokens", 0)),
            output_tokens=usage.get("completion_tokens", usage.get("output_tokens", 0)),
            conversation_id=conversation_id,
        )

        # Persist conversation
        if not conversation_id:
            conv = await self._conv_repo.create_conversation(
                user_id=user_id,
                title=question[:80],
            )
            conversation_id = conv.id

        await self._conv_repo.add_message(conversation_id, "user", question)
        await self._conv_repo.add_message(conversation_id, "assistant", answer, sources=citations)

        response = ChatResponse(
            conversation_id=conversation_id,
            answer=answer,
            citations=citations,
        )

        # Cache only new conversations
        set_cached_response(question, user_id, response.model_dump())
        return response

    async def get_history(self, conversation_id: str, user_id: str):
        conv = await self._conv_repo.get_by_id(conversation_id, user_id)
        if not conv:
            raise NotFoundException(ErrorCode.CONVERSATION_NOT_FOUND, "Conversation not found")
        return conv

    async def list_conversations(self, user_id: str):
        return await self._conv_repo.list_by_user(user_id)
