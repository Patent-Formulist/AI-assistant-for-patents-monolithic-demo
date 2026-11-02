from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from temporalio import activity

from app.temporal import shared
from core.dependencies.analog.analog_link import (
    get_analog_link_for_analog_processor,
    get_analog_link_for_patent_processor,
)
from core.dependencies.analog.analog_metadata import (
    get_analog_metadata_for_analog_processor,
    get_analog_metadata_for_patent_processor,
)


class AnalogSearchActivities:
    """Analog search steps: Rospatent link search and metadata enrichment.

    Every activity builds its processor on a fresh session; the processors own
    their transactions (ADR 0002) and are idempotent, so retries are safe.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    @activity.defn(name=shared.FIND_PATENT_ANALOG_LINKS)
    async def find_patent_analog_links(self, patent_id: int) -> None:
        async with self._session_factory() as session:
            processor = get_analog_link_for_patent_processor(db=session)
            await processor.process_parsing_links(patent_id=patent_id)

    @activity.defn(name=shared.ENRICH_PATENT_ANALOGS_METADATA)
    async def enrich_patent_analogs_metadata(self, patent_id: int) -> None:
        async with self._session_factory() as session:
            processor = get_analog_metadata_for_patent_processor(db=session)
            await processor.process_parsing_metadata(patent_id=patent_id)

    @activity.defn(name=shared.FIND_ANALOG_LINK)
    async def find_analog_link(self, patent_id: int, analog_number: str) -> int:
        async with self._session_factory() as session:
            processor = get_analog_link_for_analog_processor(db=session)
            return await processor.process_parsing_link(
                patent_id=patent_id, analog_number=analog_number
            )

    @activity.defn(name=shared.ENRICH_ANALOG_METADATA)
    async def enrich_analog_metadata(self, analog_id: int) -> None:
        async with self._session_factory() as session:
            processor = get_analog_metadata_for_analog_processor(db=session)
            await processor.process_parsing_metadata(analog_id=analog_id)

    def all(self) -> list:
        return [
            self.find_patent_analog_links,
            self.enrich_patent_analogs_metadata,
            self.find_analog_link,
            self.enrich_analog_metadata,
        ]
