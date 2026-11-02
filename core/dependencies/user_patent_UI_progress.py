from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import logger
from core.dependencies.dependencies import get_db

logger = logger.get_logger(__name__)
SessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_user_patent_UI_progress_service(db: SessionDep):
    from app.service.user_patent_UI_progress.user_patent_UI_progress import (
        UserPatentUIProgressService,
    )

    return UserPatentUIProgressService(session=db)


def get_patent_progress_query(db: SessionDep):
    from app.service.user_patent_UI_progress.progress import PatentProgressQuery
    from core.dependencies.job import get_job_service

    return PatentProgressQuery(
        ui_progress_service=get_user_patent_UI_progress_service(db=db),
        job_service=get_job_service(),
    )
