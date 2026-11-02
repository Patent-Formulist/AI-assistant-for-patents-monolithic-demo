from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from temporalio import activity
from temporalio.exceptions import ApplicationError

from app.temporal import shared
from core.dependencies.identity_prototype.processor import get_processor_for_patent
from core.dependencies.patent_application import get_application_processor
from core.dependencies.pipeline import get_pipeline_preconditions
from core.exceptions import PipelinePreconditionError


class PatentPipelineActivities:
    """Single-step pipelines: identity prototype and patent application.

    Each activity runs the whole read -> LLM -> write processor on a fresh
    session; the processor replaces previous results in one transaction, so
    retries are safe.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    @activity.defn(name=shared.GENERATE_IDENTITY)
    async def generate_identity(self, patent_id: int) -> None:
        async with self._session_factory() as session:
            try:
                await get_pipeline_preconditions(db=session).check_identity(patent_id)
            except PipelinePreconditionError as e:
                # Missing data does not appear on retry
                raise ApplicationError(str(e), non_retryable=True) from e
            processor = get_processor_for_patent(db=session)
            await processor.process_generate_identify_prototype(patent_id)

    @activity.defn(name=shared.GENERATE_APPLICATION)
    async def generate_application(self, patent_id: int) -> None:
        async with self._session_factory() as session:
            processor = get_application_processor(db=session)
            await processor.generate_application(patent_id)

    def all(self) -> list:
        return [self.generate_identity, self.generate_application]
