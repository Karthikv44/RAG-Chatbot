from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from Src.Database.database import engine
from Src.Error_Codes.exceptions import AppException
from Src.Loggers.logger import get_logger
from Src.Middleware.encryption_middleware import EncryptionMiddleware
from Src.Migration.migrate import run_migrations
from Src.Observability.tracer import setup_tracing
from Src.Routers.router import api_router
from Src.Service.bm25_service import build_bm25_from_chroma

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up RAG Chatbot...")
    await run_migrations()
    logger.info("Database migrations complete")
    await build_bm25_from_chroma()
    logger.info("BM25 index ready")
    yield
    logger.info("Shutting down RAG Chatbot...")
    await engine.dispose()


app = FastAPI(
    title="RAG Chatbot API",
    version="1.0.0",
    description="RAG-powered chatbot using AWS Bedrock + ChromaDB",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Payload encryption (disabled in local, active in prod)
app.add_middleware(EncryptionMiddleware)

# OpenTelemetry tracing
setup_tracing(app, engine.sync_engine)

# Routers
app.include_router(api_router)


# Global exception handler
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error_code": exc.error_code, "message": exc.message},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500, content={"error_code": "GEN_001", "message": "Internal server error"}
    )


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}
