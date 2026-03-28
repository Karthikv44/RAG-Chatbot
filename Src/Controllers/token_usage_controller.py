from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from Src.Database.database import get_db
from Src.Middleware.auth_middleware import get_current_user_id
from Src.Repository.token_usage_repository import TokenUsageRepository
from Src.DTO.token_usage_dto import TokenUsageRecord, TokenUsageSummary

router = APIRouter(prefix="/usage", tags=["Token Usage"])


@router.get("/", response_model=list[TokenUsageRecord])
async def get_token_usage(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get all token usage records for the current user."""
    records = await TokenUsageRepository(db).get_usage_by_user(user_id)
    return [
        TokenUsageRecord(
            id=r.id,
            model_type=r.model_type,
            model_id=r.model_id,
            input_tokens=r.input_tokens,
            output_tokens=r.output_tokens,
            total_tokens=r.total_tokens,
            conversation_id=r.conversation_id,
            created_at=r.created_at.isoformat(),
        )
        for r in records
    ]


@router.get("/summary", response_model=list[TokenUsageSummary])
async def get_token_usage_summary(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get aggregated token usage grouped by model for the current user."""
    return await TokenUsageRepository(db).get_usage_summary(user_id)
