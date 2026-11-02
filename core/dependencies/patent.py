from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies.dependencies import get_db

SessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_patent_service(db: SessionDep):
    from app.service.patent.patent import PatentService

    return PatentService(session=db)
