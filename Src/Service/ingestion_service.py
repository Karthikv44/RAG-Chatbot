"""
Document ingestion service.
Loads PDF/Markdown files, chunks them, and stores in ChromaDB.
Captures embedding token usage per ingestion.
"""
import os
from langchain_community.document_loaders import PyPDFLoader, UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from sqlalchemy.ext.asyncio import AsyncSession

from Src.Repository.vector_repository import ChromaVectorRepository
from Src.Repository.token_usage_repository import TokenUsageRepository
from Src.Service.bedrock_factory import get_embedding_model
from Src.Config.config import get_settings
from Src.Error_Codes.exceptions import IngestionException, ErrorCode
from Src.Loggers.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

CHUNK_SIZE = 600
CHUNK_OVERLAP = 100
SUPPORTED_EXTENSIONS = {".pdf", ".md", ".txt"}

# Titan v2 uses ~1 token per 4 chars (approximate for tracking)
def _estimate_tokens(text: str) -> int:
    return max(1, len(text) // 4)


class IngestionService:
    def __init__(self, db: AsyncSession, user_id: str):
        self._vector_repo = ChromaVectorRepository(get_embedding_model())
        self._token_repo = TokenUsageRepository(db)
        self._user_id = user_id
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
        )

    def _load_documents(self, file_path: str) -> list[Document]:
        ext = os.path.splitext(file_path)[-1].lower()
        if ext not in SUPPORTED_EXTENSIONS:
            raise IngestionException(
                ErrorCode.UNSUPPORTED_FILE_TYPE,
                f"Unsupported file type: {ext}. Supported: {SUPPORTED_EXTENSIONS}",
            )
        if ext == ".pdf":
            loader = PyPDFLoader(file_path)
        elif ext == ".md":
            loader = UnstructuredMarkdownLoader(file_path)
        else:
            from langchain_community.document_loaders import TextLoader
            loader = TextLoader(file_path)
        return loader.load()

    async def ingest_file(self, file_path: str) -> dict:
        try:
            logger.info(f"Starting ingestion for: {file_path}")
            raw_docs = self._load_documents(file_path)
            chunks = self._splitter.split_documents(raw_docs)

            # Estimate total tokens sent to embedding model
            total_chars = sum(len(c.page_content) for c in chunks)
            estimated_tokens = _estimate_tokens(total_chars)

            count = await self._vector_repo.add_documents(chunks)

            # Record embedding token usage
            await self._token_repo.record(
                user_id=self._user_id,
                model_id=settings.bedrock_embedding_model_id,
                model_type="embedding",
                input_tokens=estimated_tokens,
                output_tokens=0,
            )

            logger.info(f"Ingested {count} chunks from {file_path}")
            return {"chunks_stored": count, "document_name": os.path.basename(file_path)}
        except IngestionException:
            raise
        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            raise IngestionException(ErrorCode.INGESTION_FAILED, str(e))
