from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import logger
from core.dependencies.attribute import get_attribute_service
from core.dependencies.dependencies import get_db, get_unit_of_work

logger = logger.get_logger(__name__)
SessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_statistics_service(db: SessionDep):
    from app.service.statistics.statistics import StatisticsService

    return StatisticsService(session=db)


def get_statistics_frontend_query(db: SessionDep):
    from app.service.statistics.frontend import StatisticsFrontendQuery

    return StatisticsFrontendQuery(
        statistics_service=get_statistics_service(db=db),
        attribute_service=get_attribute_service(db=db),
    )


@lru_cache
def get_checking_analog_generator():
    from app.service.statistics.coincidence.raw_data_generator.checking_analog import (
        CheckingAnalogGenerator,
    )
    from core.dependencies.factories import get_llm_client_deepseek, get_prompt_manager

    return CheckingAnalogGenerator(
        llm_client=get_llm_client_deepseek(),
        prompt_manager=get_prompt_manager(),
    )


@lru_cache
def get_checking_patent_generator():
    from app.service.statistics.coincidence.raw_data_generator.checking_patent import (
        CheckingPatentGenerator,
    )
    from core.dependencies.factories import get_llm_client_deepseek, get_prompt_manager

    return CheckingPatentGenerator(
        llm_client=get_llm_client_deepseek(),
        prompt_manager=get_prompt_manager(),
    )


def get_processor_analog_coincidence(db: SessionDep):
    from app.service.statistics.coincidence.processor.analog_coincidence import (
        ProcessorAnalogCoincidencesService,
    )
    from core.dependencies.analog.analog import get_analog_service

    return ProcessorAnalogCoincidencesService(
        uow=get_unit_of_work(db=db),
        analog_service=get_analog_service(db=db),
        statistics_service=get_statistics_service(db=db),
        attribute_service=get_attribute_service(db=db),
        generator=get_checking_analog_generator(),
    )


def get_processor_patent_coincidence(db: SessionDep):
    from app.service.statistics.coincidence.processor.patent_coincidence import (
        ProcessorPatentCoincidencesService,
    )
    from core.dependencies.patent import get_patent_service

    return ProcessorPatentCoincidencesService(
        uow=get_unit_of_work(db=db),
        patent_service=get_patent_service(db=db),
        statistics_service=get_statistics_service(db=db),
        attribute_service=get_attribute_service(db=db),
        generator=get_checking_patent_generator(),
    )


@lru_cache
def get_patent_attribute_raw_data_generator():
    from app.service.statistics.attribute_generator.raw_data_generator.patent_attribute import (
        PatentAttributeGenerator,
    )
    from core.dependencies.factories import get_llm_client_deepseek, get_prompt_manager

    return PatentAttributeGenerator(
        llm_client=get_llm_client_deepseek(),
        prompt_manager=get_prompt_manager(),
    )


@lru_cache
def get_analog_attribute_raw_data_generator():
    from app.service.statistics.attribute_generator.raw_data_generator.analog_attribute import (
        AnalogAttributeGenerator,
    )
    from core.dependencies.factories import get_llm_client_deepseek, get_prompt_manager

    return AnalogAttributeGenerator(
        llm_client=get_llm_client_deepseek(),
        prompt_manager=get_prompt_manager(),
    )


@lru_cache
def get_general_attribute_raw_data_generator():
    from app.service.statistics.attribute_generator.raw_data_generator.general_attribute import (
        GeneralAttributeGenerator,
    )
    from core.dependencies.factories import get_llm_client_deepseek, get_prompt_manager

    return GeneralAttributeGenerator(
        llm_client=get_llm_client_deepseek(),
        prompt_manager=get_prompt_manager(),
    )


@lru_cache
def get_matching_analog_attribute_raw_data_generator():
    from app.service.statistics.attribute_generator.raw_data_generator.matching_analog_attributes import (
        MatchingAnalogAttributeGenerator,
    )
    from core.dependencies.factories import get_llm_client_deepseek, get_prompt_manager

    return MatchingAnalogAttributeGenerator(
        llm_client=get_llm_client_deepseek(),
        prompt_manager=get_prompt_manager(),
    )


def get_processor_patent_attribute(db: SessionDep):
    from app.service.statistics.attribute_generator.processor.patent_attribute import (
        ProcessorPatentAttributeService,
    )
    from core.dependencies.patent import get_patent_service

    return ProcessorPatentAttributeService(
        uow=get_unit_of_work(db=db),
        patent_service=get_patent_service(db=db),
        attribute_service=get_attribute_service(db=db),
        generator=get_patent_attribute_raw_data_generator(),
    )


def get_processor_analog_attribute(db: SessionDep):
    from app.service.statistics.attribute_generator.processor.analog_attribute import (
        ProcessorAnalogAttributeService,
    )
    from core.dependencies.analog.analog import get_analog_service

    return ProcessorAnalogAttributeService(
        uow=get_unit_of_work(db=db),
        analog_service=get_analog_service(db=db),
        generator=get_analog_attribute_raw_data_generator(),
        attribute_service=get_attribute_service(db=db),
    )


def get_processor_general_attribute(db: SessionDep):
    from app.service.statistics.attribute_generator.processor.general_attribute import (
        ProcessorGeneralAttributeService,
    )

    return ProcessorGeneralAttributeService(
        uow=get_unit_of_work(db=db),
        attribute_service=get_attribute_service(db=db),
        generator=get_general_attribute_raw_data_generator(),
    )


def get_processor_matching_analog_attribute(db: SessionDep):
    from app.service.statistics.attribute_generator.processor.matching_analog_attributes import (
        ProcessorMatchingAnalogAttributeService,
    )

    return ProcessorMatchingAnalogAttributeService(
        uow=get_unit_of_work(db=db),
        attribute_service=get_attribute_service(db=db),
        generator=get_matching_analog_attribute_raw_data_generator(),
    )


def get_statistics_processor(db: SessionDep):
    from app.service.statistics.processor.statistics import ProcessorStatisticsService
    from app.temporal.client import WorkflowStarter
    from core.dependencies.billing import get_billing_service
    from core.dependencies.job import get_job_service
    from core.dependencies.pipeline import get_pipeline_preconditions
    from core.dependencies.task import get_task_service

    return ProcessorStatisticsService(
        job_service=get_job_service(),
        task_service=get_task_service(),
        workflow_starter=WorkflowStarter(),
        billing=get_billing_service(),
        preconditions=get_pipeline_preconditions(db=db),
    )
