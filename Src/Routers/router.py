from fastapi import APIRouter

from Src.Controllers.auth_controller import router as auth_router
from Src.Controllers.chat_controller import router as chat_router
from Src.Controllers.ingestion_controller import router as ingestion_router
from Src.Controllers.prompt_controller import router as prompt_router
from Src.Controllers.token_usage_controller import router as token_usage_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(ingestion_router)
api_router.include_router(chat_router)
api_router.include_router(token_usage_router)
api_router.include_router(prompt_router)
