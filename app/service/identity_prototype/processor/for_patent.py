from app.service.attribute.attribute import AttributeService
from app.service.identity_prototype.identity_prototype import IdentifyPrototypeService
from app.service.identity_prototype.processor.data_fetcher import IdentityDataFetcher
from app.service.identity_prototype.processor.domain_builder import (
    IdentifyDomainBuilder,
)
from app.service.identity_prototype.raw_data_generator.identify_prototype import (
    IdentityGenerator,
)
from app.service.processor import UnitOfWork
from core import logger
from core.domain.attribute import Attribute
from core.domain.identify_prototype import IdentityPrototype
from core.enum.attribute_type import AttributeType
from core.exceptions import IdentityGenerationError

logger = logger.get_logger(__name__)


class PatentIdentityProcessor:
    """Identity prototype for a patent: read -> LLM -> write in one transaction (ADR 0002)."""

    def __init__(
        self,
        uow: UnitOfWork,
        data_fetcher: IdentityDataFetcher,
        builder: IdentifyDomainBuilder,
        i_service: IdentifyPrototypeService,
        a_service: AttributeService,
        generator: IdentityGenerator,
    ):
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    async def process_generate_identify_prototype(self, patent_id: int) -> None:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")




