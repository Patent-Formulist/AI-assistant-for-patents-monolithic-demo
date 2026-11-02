from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies.dependencies import get_db

SessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_patent_access(db: SessionDep):
    from app.service.access import PatentAccess

    return PatentAccess(session=db)
