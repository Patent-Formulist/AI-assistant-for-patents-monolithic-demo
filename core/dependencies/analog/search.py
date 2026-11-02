from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import logger
from core.dependencies.dependencies import get_db

logger = logger.get_logger(__name__)
SessionDep = Annotated[AsyncSession, Depends(get_db)]


@lru_cache
def get_component_analog_search():
    from app.service.analog.table.component_generator.search import (
        AnalogSearchComponentGenerator,
    )

    return AnalogSearchComponentGenerator()


def get_analog_search_processor():
    from app.service.analog.search.analog_search import ProcessorAnalogSearchService
    from app.temporal.client import WorkflowStarter
    from core.dependencies.billing import get_billing_service
    from core.dependencies.job import get_job_service
    from core.dependencies.task import get_task_service

    return ProcessorAnalogSearchService(
        job_service=get_job_service(),
        task_service=get_task_service(),
        workflow_starter=WorkflowStarter(),
        billing=get_billing_service(),
    )


def get_search_edit_orchestrator(db: SessionDep):
    from app.service.analog.search.edit_orchestrator import (
        SearchEditOrchestratorService,
    )
    from core.dependencies.access import get_patent_access
    from core.dependencies.analog.analog import get_analog_service
    from core.dependencies.dependencies import get_unit_of_work

    return SearchEditOrchestratorService(
        uow=get_unit_of_work(db=db),
        analog_service=get_analog_service(db=db),
        access=get_patent_access(db=db),
    )
