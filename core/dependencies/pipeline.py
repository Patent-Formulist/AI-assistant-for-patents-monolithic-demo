from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies.dependencies import get_db

SessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_pipeline_preconditions(db: SessionDep):
    from app.service.pipeline_preconditions import PipelinePreconditions
    from core.dependencies.analog.analog import get_analog_service
    from core.dependencies.patent import get_patent_service
    from core.dependencies.statistics import get_statistics_service

    return PipelinePreconditions(
        analog_service=get_analog_service(db=db),
        statistics_service=get_statistics_service(db=db),
        patent_service=get_patent_service(db=db),
    )
