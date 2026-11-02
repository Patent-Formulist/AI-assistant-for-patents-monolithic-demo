from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import logger
from core.dependencies.dependencies import get_db

logger = logger.get_logger(__name__)
SessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_data_fetcher(db: SessionDep):
    from app.service.identity_prototype.processor.data_fetcher import (
        IdentityDataFetcher,
    )
    from core.dependencies.analog.analog import get_analog_service
    from core.dependencies.attribute import get_attribute_service
    from core.dependencies.patent import get_patent_service
    from core.dependencies.statistics import get_statistics_service

    return IdentityDataFetcher(
        statistics_service=get_statistics_service(db),
        attribute_service=get_attribute_service(db),
        analog_service=get_analog_service(db),
        patent_service=get_patent_service(db),
    )


@lru_cache
def get_domain_builder():
    from app.service.identity_prototype.processor.domain_builder import (
        IdentifyDomainBuilder,
    )

    return IdentifyDomainBuilder()


def get_processor_for_patent(db: SessionDep):
    from app.service.identity_prototype.processor.for_patent import (
        PatentIdentityProcessor,
    )
    from core.dependencies.attribute import get_attribute_service
    from core.dependencies.dependencies import get_unit_of_work
    from core.dependencies.identity_prototype.raw_data_generator import (
        get_identify_prototype,
    )
    from core.dependencies.identity_prototype.service import (
        get_identify_prototype_service,
    )

    return PatentIdentityProcessor(
        generator=get_identify_prototype(),
        uow=get_unit_of_work(db=db),
        data_fetcher=get_data_fetcher(db),
        builder=get_domain_builder(),
        i_service=get_identify_prototype_service(db),
        a_service=get_attribute_service(db),
    )


def get_identity_pipeline(db: SessionDep):
    from app.service.identity_prototype.processor.pipeline import ProcessorIdentityPipelineService
    from app.temporal.client import WorkflowStarter
    from core.dependencies.billing import get_billing_service
    from core.dependencies.job import get_job_service
    from core.dependencies.pipeline import get_pipeline_preconditions
    from core.dependencies.task import get_task_service

    return ProcessorIdentityPipelineService(
        job_service=get_job_service(),
        task_service=get_task_service(),
        workflow_starter=WorkflowStarter(),
        billing=get_billing_service(),
        preconditions=get_pipeline_preconditions(db=db),
    )
