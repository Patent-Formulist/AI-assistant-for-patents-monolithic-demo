from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import logger
from core.dependencies.dependencies import get_db

logger = logger.get_logger(__name__)
SessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_identify_prototype_service(db: SessionDep):
    from app.service.identity_prototype.identity_prototype import (
        IdentifyPrototypeService,
    )

    return IdentifyPrototypeService(session=db)
