from app.service.analog.analog import AnalogService
from app.service.analog.analog_metadata.raw_data_generator.analog_metadata import (
    MetaGenerator,
)
from app.service.processor import Processor, UnitOfWork
from core import logger
from core.domain.analog import Analog
from core.exceptions import (
    AnalogsCreationMetadataError,
    PatentAnalogsCreationMetadataError,
)

logger = logger.get_logger(__name__)


class ProcessorPatentAnalogsMetadataService(Processor):
    """Processor for enriching analogues with metadata (abstract, claims, description)"""

    def __init__(self, uow: UnitOfWork, analog_service: AnalogService, generator: MetaGenerator):
        """
        Args:
            uow: Transaction boundary shared with the services
            analog_service: Analog service
            generator: Generator of metadata for similar patents
        """
        super().__init__(uow=uow, error_class=PatentAnalogsCreationMetadataError)
        self._analog_service = analog_service
        self._generator = generator

    async def process_parsing_metadata(self, patent_id: int) -> None:
        """
        Create and save metadata for analogues of a patent.

        Args:
            patent_id: Patent ID
        """
        await self._run(
            operation=self._process_metadata_logic,
            operation_name="analogs_metadata_creation",
            patent_id=patent_id,
        )

    async def _process_metadata_logic(self, patent_id: int) -> None:
        # Read
        async with self._uow:
            analogs: list[Analog] = await self._analog_service.get_analogs(patent_id)

        if not analogs:
            logger.warning(f"No analogues found for patent {patent_id}")
            return

        # Parse metadata outside the transaction
        enriched = await self._generate_metadata(analogs, patent_id)

        # Write
        async with self._uow:
            await self._analog_service.update_metadata(enriched)
        logger.info(f"Updated {len(enriched)} analogues with metadata")

    async def _generate_metadata(self, analogs: list[Analog], patent_id: int) -> list[Analog]:
        """Generate metadata for analogues"""
        enriched = await self._generator.generate_data_for_analogs(analogs)

        if not enriched:
            error_msg = f"No metadata generated for patent {patent_id}"
            logger.error(error_msg)
            raise AnalogsCreationMetadataError(error_msg)

        logger.info(f"Generated metadata for {len(enriched)} analogues")
        return enriched
