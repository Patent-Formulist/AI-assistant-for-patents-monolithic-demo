from app.service.analog.analog import AnalogService
from app.service.analog.analog_link.parser.rospatent_link_parser import (
    RospatentLinkParser,
)
from app.service.analog.analog_link.processor.analog_link import ProcessorLinksService
from app.service.patent.patent import PatentService
from app.service.processor import UnitOfWork
from core import logger
from core.domain.analog import Analog
from core.exceptions import PatentAnalogsCreationLinkError

logger = logger.get_logger(__name__)


class ProcessorPatentAnalogsLinksService(ProcessorLinksService):
    """
    Processor for creating links to analogues.
    """

    def __init__(
        self,
        uow: UnitOfWork,
        patent_service: PatentService,
        analog_service: AnalogService,
        parser: RospatentLinkParser,
    ):
        """
        Args:
            uow: Transaction boundary shared with the services
            patent_service: Patent service
            analog_service: Analog service
            parser: Parser of links to similar patents
        """
        super().__init__(
            uow=uow,
            analog_service=analog_service,
            parser=parser,
            error_class=PatentAnalogsCreationLinkError,
        )
        self._patent_service = patent_service

    async def process_parsing_links(self, patent_id: int) -> None:
        """
        Creating and saving links to analogues for a patent.

        Args:
            patent_id: Patent ID
        """
        await self._run(
            operation=self._process_links_logic,
            operation_name="analog_links_creation",
            patent_id=patent_id,
        )

    async def _process_links_logic(self, patent_id: int) -> None:
        # Read
        async with self._uow:
            patent = await self._patent_service.get_patent(patent_id)

        # Parse outside the transaction
        analogs: list[Analog] = await self._process_parsing(patent.search_query)
        logger.info(f"Found {len(analogs)} analogs")
        if not analogs:
            return

        # Write: reuse analogs known by number, create the rest, link all to the patent
        async with self._uow:
            existing_ids, new_analogs = await self._split_existing_and_new_analogs(
                patent_id, analogs
            )
            created = await self._analog_service.create_analogs(new_analogs)
            await self._analog_service.link_to_patent(
                patent_id, existing_ids + [a.id for a in created]
            )

    async def _split_existing_and_new_analogs(
        self, patent_id: int, analogs: list[Analog]
    ) -> tuple[list[int], list[Analog]]:
        """Split analogs into the patent's existing ones (by number) and new ones."""
        existing = await self._analog_service.get_analogs_by_numbers(
            patent_id, [a.analog_num for a in analogs]
        )

        existing_ids = []
        new_analogs = []
        for analog in analogs:
            if analog.analog_num in existing:
                existing_ids.append(existing[analog.analog_num].id)
            else:
                new_analogs.append(analog)

        return existing_ids, new_analogs
