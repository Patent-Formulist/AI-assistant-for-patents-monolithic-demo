from app.service.analog.analog_metadata.parser.metadata_patent_analog_rospatent import (
    RospatentMetadataParser,
)
from core import logger
from core.domain.analog import Analog
from core.dto.patent_info import PatentDocument
from core.exceptions import ParserError, ServiceRawDataGeneratorError, ValidationError

logger = logger.get_logger(__name__)


class MetaGenerator:
    """Generator of metadata for patent analogs"""

    def __init__(self, parser_service: RospatentMetadataParser):
        self._parser_service: RospatentMetadataParser = parser_service

    async def generate_data_for_analogs(self, analogs: list[Analog]) -> list[Analog]:
        """Enrich the provided analogs with metadata using their links."""
        if not analogs:
            logger.warning("Empty analogs list provided")
            return []
        logger.info(f"Starting metadata generation for {len(analogs)} analogs")
        try:
            # Prepare links for parsing
            analog_links = self._prepare_analog_links(analogs)
            # Parse metadata
            metadata = await self._parser_service.parse_for_analogs(analog_links)
            # Enrich analogs with metadata
            enriched_analogs = self._enrich_analogs(analogs, metadata)
            logger.info(
                f"Metadata generation completed:"
                f" {MetaGenerator._get_enriched_count(enriched_analogs)}/{len(analogs)} analogs enriched"
            )
            return enriched_analogs

        except (ParserError, ValidationError) as e:
            logger.error(f"Parser/validation error in metadata generation: {e}")
            raise ServiceRawDataGeneratorError(f"Metadata generation failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error in metadata generation: {e}", exc_info=True)
            raise ServiceRawDataGeneratorError(
                f"Unexpected error in metadata generation: {e}"
            ) from e

    async def generate_data_for_analog(self, analog: Analog) -> None:
        """Create an Analog instance for analog and fill it with metadata."""
        logger.info(f"Starting metadata generation for analog number: {analog.analog_num}")
        try:
            # Parse metadata for a single patent number
            metadata = await self._parser_service.parse_for_analog(analog)
            # Fill analog fields with metadata
            MetaGenerator._fill_analog_fields(analog, metadata)
            logger.info("Metadata generation completed")
        except (ParserError, ValidationError) as e:
            logger.error(f"Parser/validation error in metadata generation: {e}")
            raise ServiceRawDataGeneratorError(f"Metadata generation failed: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error in metadata generation: {e}", exc_info=True)
            raise ServiceRawDataGeneratorError(
                f"Unexpected error in metadata generation: {e}"
            ) from e

    def _prepare_analog_links(self, analogs: list[Analog]) -> dict[str, str]:
        """Build a dictionary mapping analog numbers to their page URLs."""
        analog_links = {}
        for analog in analogs:
            analog_links[analog.analog_num] = analog.analog_link
        return analog_links

    @staticmethod
    def _get_enriched_count(enriched_analogs: list[Analog]) -> int:
        """Count how many analogs have at least one of abstract/claims/description filled."""
        return sum(1 for a in enriched_analogs if a.abstract or a.claims or a.description)

    @staticmethod
    def _enrich_analogs(analogs: list[Analog], metadata: dict[str, PatentDocument]) -> list[Analog]:
        """Populate each analog with the corresponding metadata and return the modified list."""
        for analog in analogs:
            patent_metadata = metadata.get(analog.analog_num)
            MetaGenerator._fill_analog_fields(analog, patent_metadata)
        return analogs

    @staticmethod
    def _fill_analog_fields(analog: Analog, patent_metadata: PatentDocument) -> None:
        """Set abstract, claims, and description fields on the analog object."""
        if patent_metadata:
            analog.abstract = getattr(patent_metadata, "abstract", "")
            analog.claims = getattr(patent_metadata, "claims", "")
            analog.description = getattr(patent_metadata, "description", "")
        else:
            logger.debug(f"No metadata found for analog {analog.analog_num}")
            analog.abstract = ""
            analog.claims = ""
            analog.description = ""
