from core.dependencies.dependencies import get_db


async def with_db(func, *args, **kwargs):
    """Выполняет функцию func с сессией из get_db"""
    async for session in get_db():
        return await func(session, *args, **kwargs)
