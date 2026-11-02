from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core.dependencies.dependencies import get_db

SessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_application_service(db: SessionDep):
    from app.service.patent_application.service import PatentApplicationService

    return PatentApplicationService(session=db)


@lru_cache
def get_application_generator():
    from app.service.patent_application.generator import PatentApplicationGenerator
    from core.dependencies.factories import get_llm_client_deepseek

    return PatentApplicationGenerator(llm_client=get_llm_client_deepseek())


def get_application_processor(db: SessionDep):
    from app.service.patent_application.processor import ProcessorPatentApplicationService
    from core.dependencies.analog.analog import get_analog_service
    from core.dependencies.dependencies import get_unit_of_work
    from core.dependencies.drawing import get_drawing_service
    from core.dependencies.identity_prototype.service import (
        get_identify_prototype_service,
    )
    from core.dependencies.patent import get_patent_service

    return ProcessorPatentApplicationService(
        uow=get_unit_of_work(db=db),
        application_service=get_application_service(db=db),
        patent_service=get_patent_service(db=db),
        drawing_service=get_drawing_service(db=db),
        identify_prototype_service=get_identify_prototype_service(db=db),
        analog_service=get_analog_service(db=db),
        generator=get_application_generator(),
    )


def get_application_pipeline():
    from app.service.patent_application.pipeline import ProcessorApplicationPipelineService
    from app.temporal.client import WorkflowStarter
    from core.dependencies.billing import get_billing_service
    from core.dependencies.job import get_job_service
    from core.dependencies.task import get_task_service

    return ProcessorApplicationPipelineService(
        job_service=get_job_service(),
        task_service=get_task_service(),
        workflow_starter=WorkflowStarter(),
        billing=get_billing_service(),
    )
