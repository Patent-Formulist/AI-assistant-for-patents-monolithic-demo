from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import logger
from core.dependencies.dependencies import get_db
from core.settings import get_settings

logger = logger.get_logger(__name__)
SessionDep = Annotated[AsyncSession, Depends(get_db)]


@lru_cache
def get_prompt_manager():
    from core.manager_prompt.prompt_manager import PromptManager

    return PromptManager(get_settings().storage)


@lru_cache
def get_llm_client_deepseek():
    from app.service.llm_client.deepseek import DeepSeekClient

    return DeepSeekClient(config=get_settings().llm.deepseek)


# ============ Table Writers (stateless, saved in cache) ===============


@lru_cache
def get_csv_writer():
    from app.service.table.writer.csv_writer import CSVTableWriter

    return CSVTableWriter()


@lru_cache
def get_xlsx_writer():
    from app.service.table.writer.xlsx_writer import XLSXTableWriter

    return XLSXTableWriter()
