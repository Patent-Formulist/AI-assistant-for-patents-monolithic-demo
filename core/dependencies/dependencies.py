from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    from core.db.db import get_db_instance

    db = get_db_instance()
    if db is None:
        raise RuntimeError("Database not initialized")
    async for session in db.get_db():
        yield session


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    from core.db.db import get_db_instance

    db = get_db_instance()
    if db is None:
        raise RuntimeError("Database not initialized")
    return db.session_factory


def get_unit_of_work(db: AsyncSession):
    from app.service.processor import UnitOfWork

    return UnitOfWork(session=db)
