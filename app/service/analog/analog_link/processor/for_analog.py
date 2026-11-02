from app.service.analog.analog import AnalogService
from app.service.analog.analog_link.parser.rospatent_link_parser import (
    RospatentLinkParser,
)
from app.service.analog.analog_link.processor.analog_link import ProcessorLinksService
from app.service.processor import UnitOfWork
from core import logger
from core.domain.analog import Analog
from core.exceptions import PatentAnalogsCreationLinkError

logger = logger.get_logger(__name__)


class ProcessorPatentAnalogLinksService(ProcessorLinksService):
    """
    Processor for creating link to analog.
    """

    def __init__(
        self,
        uow: UnitOfWork,
        analog_service: AnalogService,
        parser: RospatentLinkParser,
    ):
        """
        Args:
            uow: Transaction boundary shared with the services
            analog_service: Analog service
            parser: Parser of links to similar patents
        """
        super().__init__(
            uow=uow,
            analog_service=analog_service,
            parser=parser,
            error_class=PatentAnalogsCreationLinkError,
        )

    async def process_parsing_link(self, patent_id: int, analog_number: str) -> int:
        """
        Creating and saving link to analog for a patent.

        Args:
            patent_id: Patent ID
            analog_number: Analog number

        Returns:
            ID of the created analog
        """
        return await self._run(
            operation=self._process_links_logic,
            operation_name="analog_links_creation",
            patent_id=patent_id,
            analog_number=analog_number,
        )

    async def _process_links_logic(self, patent_id: int, analog_number: str) -> int:
        # Parse outside the transaction
        analogs: list[Analog] = await self._process_parsing(number=analog_number)
        logger.info(f"Found {len(analogs)} analogs")

        # Write: reuse the patent's analog with this number (a retried step must not
        # create a duplicate), otherwise create it; then link it to the patent
        async with self._uow:
            found = analogs[0]
            existing = await self._analog_service.get_analogs_by_numbers(
                patent_id, [found.analog_num]
            )
            analog: Analog = existing.get(found.analog_num) or (
                await self._analog_service.create_analog(found)
            )
            await self._analog_service.link_to_patent(patent_id, [analog.id])

        return analog.id
