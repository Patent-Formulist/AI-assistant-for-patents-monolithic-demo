from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from temporalio import activity
from temporalio.exceptions import ApplicationError

from app.temporal import shared
from core.dependencies.pipeline import get_pipeline_preconditions
from core.dependencies.statistics import (
    get_processor_analog_attribute,
    get_processor_analog_coincidence,
    get_processor_general_attribute,
    get_processor_matching_analog_attribute,
    get_processor_patent_attribute,
    get_processor_patent_coincidence,
)
from core.exceptions import PipelinePreconditionError


class StatisticsActivities:
    """Statistics steps: attributes via LLM, then coincidences.

    Every activity builds its processor on a fresh session; the processors own
    their transactions and replace previous results (ADR 0002), so retries are safe.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    @activity.defn(name=shared.GENERATE_ANALOG_ATTRIBUTES)
    async def generate_analog_attributes(
        self, patent_id: int, analog_ids: list[int] | None = None
    ) -> None:
        async with self._session_factory() as session:
            try:
                await get_pipeline_preconditions(db=session).check_statistics(patent_id)
            except PipelinePreconditionError as e:
                # Missing data does not appear on retry
                raise ApplicationError(str(e), non_retryable=True) from e
            processor = get_processor_analog_attribute(db=session)
            await processor.process_generate_analog_attribute(
                patent_id=patent_id, analog_ids=analog_ids
            )

    @activity.defn(name=shared.MATCH_ANALOG_ATTRIBUTES)
    async def match_analog_attributes(self, patent_id: int) -> None:
        async with self._session_factory() as session:
            processor = get_processor_matching_analog_attribute(db=session)
            await processor.process_generate_matcher_analog_attribute(patent_id=patent_id)

    @activity.defn(name=shared.GENERATE_PATENT_ATTRIBUTES)
    async def generate_patent_attributes(self, patent_id: int) -> None:
        async with self._session_factory() as session:
            processor = get_processor_patent_attribute(db=session)
            await processor.process_generate_patent_attribute(patent_id=patent_id)

    @activity.defn(name=shared.GENERATE_GENERAL_ATTRIBUTES)
    async def generate_general_attributes(self, patent_id: int) -> None:
        async with self._session_factory() as session:
            processor = get_processor_general_attribute(db=session)
            await processor.process_generate_general_attribute(patent_id=patent_id)

    @activity.defn(name=shared.GENERATE_ANALOG_COINCIDENCES)
    async def generate_analog_coincidences(self, patent_id: int) -> None:
        async with self._session_factory() as session:
            processor = get_processor_analog_coincidence(db=session)
            await processor.process_generate_analog_coincidences(patent_id=patent_id)

    @activity.defn(name=shared.GENERATE_PATENT_COINCIDENCES)
    async def generate_patent_coincidences(self, patent_id: int) -> None:
        async with self._session_factory() as session:
            processor = get_processor_patent_coincidence(db=session)
            await processor.process_generate_patent_coincidences(patent_id=patent_id)

    def all(self) -> list:
        return [
            self.generate_analog_attributes,
            self.match_analog_attributes,
            self.generate_patent_attributes,
            self.generate_general_attributes,
            self.generate_analog_coincidences,
            self.generate_patent_coincidences,
        ]
