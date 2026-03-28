from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from Src.Repository.Models.conversation_model import Conversation, Message


class ConversationRepository:
    def __init__(self, db: AsyncSession):
        self._db = db

    async def create_conversation(self, user_id: str, title: str | None = None) -> Conversation:
        conv = Conversation(user_id=user_id, title=title)
        self._db.add(conv)
        await self._db.flush()
        return conv

    async def get_by_id(self, conversation_id: str, user_id: str) -> Conversation | None:
        result = await self._db.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages))
            .where(Conversation.id == conversation_id, Conversation.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def list_by_user(self, user_id: str) -> list[Conversation]:
        result = await self._db.execute(
            select(Conversation)
            .where(Conversation.user_id == user_id)
            .order_by(Conversation.created_at.desc())
        )
        return list(result.scalars().all())

    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        sources: list | None = None,
    ) -> Message:
        msg = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            sources=sources,
        )
        self._db.add(msg)
        await self._db.flush()
        return msg
