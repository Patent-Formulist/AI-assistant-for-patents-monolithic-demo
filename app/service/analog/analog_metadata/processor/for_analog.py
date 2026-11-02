from app.service.analog.analog import AnalogService
from app.service.analog.analog_metadata.raw_data_generator.analog_metadata import (
    MetaGenerator,
)
from app.service.processor import Processor, UnitOfWork
from core import logger
from core.exceptions import PatentAnalogsCreationMetadataError

logger = logger.get_logger(__name__)


class ProcessorPatentAnalogMetadataService(Processor):
    """Processor for enriching analog with metadata (abstract, claims, description)"""

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

    async def process_parsing_metadata(self, analog_id: int) -> None:
        """
        Create and save metadata for an analog.

        Args:
            analog_id: Analog ID
        """
        await self._run(
            operation=self._process_metadata_logic,
            operation_name="analog_metadata_creation",
            analog_id=analog_id,
        )

    async def _process_metadata_logic(self, analog_id: int) -> None:
        # Read
        async with self._uow:
            analog = await self._analog_service.get_analog(analog_id)

        # Fill metadata from the parser outside the transaction
        await self._generator.generate_data_for_analog(analog)

        # Write
        async with self._uow:
            await self._analog_service.update_metadata([analog])
