"""
Auto migration: creates all tables on startup.
Import all models before calling run_migrations so SQLAlchemy
registers them on the Base metadata.
"""
from Src.Database.database import Base, engine
import Src.Repository.Models.user_model  # noqa: F401
import Src.Repository.Models.conversation_model  # noqa: F401
import Src.Repository.Models.token_usage_model  # noqa: F401


async def run_migrations() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
