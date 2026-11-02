from app.service.analog.analog import AnalogService
from app.service.analog.analog_link.parser.rospatent_link_parser import (
    RospatentLinkParser,
)
from app.service.processor import Processor, UnitOfWork
from core import logger
from core.domain.analog import Analog
from core.dto.patent_info import PatentSearchResult

logger = logger.get_logger(__name__)


class ProcessorLinksService(Processor):
    """
    Processor for creating links to analogues.
    """

    def __init__(
        self,
        uow: UnitOfWork,
        analog_service: AnalogService,
        parser: RospatentLinkParser,
        error_class: type[Exception],
    ):
        """
        Args:
            uow: Transaction boundary shared with the services
            analog_service: Analog service
            parser: Parser of links to similar patents
        """
        super().__init__(uow=uow, error_class=error_class)
        self._analog_service = analog_service
        self._parser = parser

    async def _process_parsing(
        self, search_query: str | None = None, number: str | None = None
    ) -> list[Analog]:
        if search_query is None:
            patents_info: list[PatentSearchResult] = await self._parser.parse_by_number(number)
        else:
            patents_info: list[PatentSearchResult] = await self._parser.parse_by_search_query(
                search_query
            )

        return [
            Analog(
                analog_num=found_analogue.patent_number,
                analog_link=found_analogue.url,
                title=found_analogue.title,
            )
            for found_analogue in patents_info
        ]
