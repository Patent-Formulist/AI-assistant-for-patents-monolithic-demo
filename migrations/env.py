import asyncio
import logging
from logging.config import fileConfig

from alembic import context
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

from core.db.db import Base
from core.db.models import *  # noqa: F403
from core.settings import get_settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

logger = logging.getLogger("alembic.env")

target_metadata = Base.metadata


def render_item(type_, obj, autogen_context):
    if type_ == "type" and obj.__class__.__module__.startswith("core."):
        autogen_context.imports.add(f"import {obj.__class__.__module__.split('.')[0]}")
    return False


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=get_settings().database.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        include_schemas=False,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    logger.info("=== STARTING MIGRATION ===")
    logger.info(f"Target metadata tables: {list(target_metadata.tables.keys())}")

    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_item=render_item,
        compare_type=True,
        compare_server_default=True,
        include_schemas=False,
    )

    with context.begin_transaction():
        context.run_migrations()
    logger.info("=== MIGRATION COMPLETED ===")


async def run_migrations_online() -> None:
    engine = create_async_engine(get_settings().database.database_url, poolclass=NullPool)
    try:
        async with engine.connect() as connection:
            await connection.run_sync(do_run_migrations)
    finally:
        await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
