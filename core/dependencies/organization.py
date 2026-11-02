from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies.dependencies import get_db

SessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_organization_service(db: SessionDep):
    from app.service.organization.organization import OrganizationService

    return OrganizationService(session=db)
