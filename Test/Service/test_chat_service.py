import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from Src.Service.chat_service import ChatService


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.mark.asyncio
async def test_chat_returns_response(mock_db):
    with (
        patch("Src.Service.chat_service.ChromaVectorRepository") as MockVec,
        patch("Src.Service.chat_service.ConversationRepository") as MockConv,
        patch("Src.Service.chat_service.get_llm"),
        patch("Src.Service.chat_service.get_embedding_model"),
        patch("Src.Service.chat_service.get_cached_response", return_value=None),
        patch("Src.Service.chat_service.set_cached_response"),
    ):
        vec = MockVec.return_value
        vec.similarity_search = AsyncMock(return_value=[
            MagicMock(page_content="context text", metadata={"source": "doc.pdf", "page": 1})
        ])

        conv_repo = MockConv.return_value
        conv_repo.create_conversation = AsyncMock(return_value=MagicMock(id="conv1"))
        conv_repo.add_message = AsyncMock()

        service = ChatService(mock_db)
        service._chain = AsyncMock()
        service._chain.ainvoke = AsyncMock(return_value="Test answer")

        result = await service.chat("What is RAG?", "user1", None)
        assert result.answer == "Test answer"
        assert result.conversation_id == "conv1"
