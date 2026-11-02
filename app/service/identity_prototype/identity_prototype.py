from app.service.base import BaseService
from app.service.identity_prototype.repository import IdentifyAttributeRepository
from core import logger
from core.data_mapper.identify_prototype.identity_prototypes import (
    IdentifyAttributesMapper,
)
from core.db.models.identify_attribute import IdentifyAttributeModel
from core.domain.identify_prototype import IdentityPrototype
from core.dto.identify_attribute import IdentifyPrototypeDto, IdentifyRowDto
from core.exceptions import (
    IdentifyPrototypeCreationError,
    IdentifyPrototypeDeleteError,
    IdentifyPrototypeGetError,
)

logger = logger.get_logger(__name__)


class IdentifyPrototypeService(BaseService[IdentifyAttributeModel, IdentifyAttributeRepository]):
    """Identified prototype of a patent: attribute comparison rows with one analog."""

    repository_type = IdentifyAttributeRepository

    async def create_identify_prototypes(
        self, identity_prototypes: list[IdentityPrototype]
    ) -> None:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    async def get_by_patent(self, patent_id: int) -> IdentifyPrototypeDto:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    async def delete_by_patent(self, patent_id: int) -> int:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    async def replace_for_patent(
        self, patent_id: int, identity_prototypes: list[IdentityPrototype]
    ) -> None:
        # Lazy: app.service.patent_application imports this service.
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")
