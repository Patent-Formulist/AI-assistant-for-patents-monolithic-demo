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
def get_token_data_service():
    from app.service.token.data import TokenDataService

    return TokenDataService(config=get_settings().auth)


def get_token_service(db: SessionDep):
    from app.service.token.token import TokenService

    return TokenService(session=db, data_service=get_token_data_service())


def get_token_processor(db: SessionDep):
    from app.service.token.processor import ProcessorTokenService

    return ProcessorTokenService(
        ds=get_token_data_service(),
        ts=get_token_service(db),
    )
