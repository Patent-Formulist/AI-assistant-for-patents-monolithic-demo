from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from core import logger
from core.settings import DatabaseSettings

logger = logger.get_logger(__name__)
Base = declarative_base()


class DB:
    def __init__(self, config_db: DatabaseSettings):
        self.config = config_db
        self._engine = None
        self._async_session_local = None

    async def init_db_client(self):
        """
        Инициализация подключения при старте приложения (startup event).
        """
        try:
            engine_kwargs = self.config.engine_kwargs
            session_kwargs = self.config.session_kwargs

            logger.info(
                f"🔌 Подключение к БД: {self.config.host}:{self.config.port}/{self.config.db_name}"
            )
            logger.debug(f"Параметры engine: {engine_kwargs}")
            logger.debug(f"Параметры session: {session_kwargs}")

            self._engine = create_async_engine(self.config.database_url, **engine_kwargs)

            self._async_session_local = async_sessionmaker(
                bind=self._engine, class_=AsyncSession, **session_kwargs
            )

            try:
                async with self._engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
            except ConnectionRefusedError:
                raise
            except Exception as e:
                logger.error(f"Ошибка при создании таблиц: {type(e).__name__}")
                raise

        except ConnectionRefusedError:
            raise
        except Exception as e:
            logger.error(f"Критическая ошибка при инициализации БД: {type(e).__name__}")
            raise

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        """Factory for short independent sessions (e.g. job/task status writes)."""
        if self._async_session_local is None:
            raise RuntimeError("Database not initialized")
        return self._async_session_local

    async def close_db_client(self):
        """Закрытие соединений при остановке приложения (shutdown event)"""
        if self._engine:
            await self._engine.dispose()
            logger.info("Db connection closed")

    async def get_db(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Возвращает объект базы данных, который можно передавать в репозитории.
        """
        async with self._async_session_local() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                try:
                    await session.close()
                except Exception:
                    pass


_db_instance: DB | None = None


def set_db_instance(db: DB | None) -> None:
    global _db_instance
    _db_instance = db


def get_db_instance() -> DB | None:
    return _db_instance
