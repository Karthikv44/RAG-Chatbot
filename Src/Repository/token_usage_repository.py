from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from Src.Repository.Models.token_usage_model import TokenUsage


class TokenUsageRepository:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def record(
        self,
        user_id: str,
        model_id: str,
        model_type: str,
        input_tokens: int,
        output_tokens: int,
        conversation_id: str | None = None,
    ) -> TokenUsage:
        record = TokenUsage(
            user_id=user_id,
            conversation_id=conversation_id,
            model_id=model_id,
            model_type=model_type,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=input_tokens + output_tokens,
        )
        self._db.add(record)
        await self._db.flush()
        return record

    async def get_usage_by_user(self, user_id: str) -> list[TokenUsage]:
        result = await self._db.execute(
            select(TokenUsage)
            .where(TokenUsage.user_id == user_id)
            .order_by(TokenUsage.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_usage_summary(self, user_id: str) -> dict:
        result = await self._db.execute(
            select(
                TokenUsage.model_type,
                TokenUsage.model_id,
                func.sum(TokenUsage.input_tokens).label("total_input"),
                func.sum(TokenUsage.output_tokens).label("total_output"),
                func.sum(TokenUsage.total_tokens).label("total_tokens"),
                func.count(TokenUsage.id).label("call_count"),
            )
            .where(TokenUsage.user_id == user_id)
            .group_by(TokenUsage.model_type, TokenUsage.model_id)
        )
        rows = result.all()
        return [
            {
                "model_type": r.model_type,
                "model_id": r.model_id,
                "total_input_tokens": r.total_input,
                "total_output_tokens": r.total_output,
                "total_tokens": r.total_tokens,
                "call_count": r.call_count,
            }
            for r in rows
        ]
