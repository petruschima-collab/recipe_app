from app.database.base import Base
from app.database.connection import (
    engine,
    AsyncSessionLocal,
    get_session,
)

from app import models


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


__all__ = [
    "Base",
    "engine",
    "AsyncSessionLocal",
    "get_session",
    "init_models",
]