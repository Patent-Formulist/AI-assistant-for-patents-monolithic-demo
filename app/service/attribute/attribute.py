from collections import defaultdict
from collections.abc import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from app.service.attribute.repository import (
    AnalogAttributeRepository,
    AttributeRepository,
    PatentAttributeRepository,
)
from app.service.base import BaseService
from core import logger
from core.data_mapper.attribute.attribute import AttributeMapper
from core.data_mapper.attribute.attributes import AttributesMapper
from core.db.models.analog_attributes import AnalogAttributeModel
from core.db.models.attribute import AttributeModel
from core.db.models.patent_attributes import PatentAttributeModel
from core.domain.attribute import Attribute
from core.domain.patent_attribute import PatentAttributeIDPair
from core.dto.analog_attribute import AnalogAttributesGroupDto
from core.dto.id_name_analog import IdNameAnalogDto
from core.enum.attribute_type import AttributeType
from core.exceptions import (
    AnalogAttributeAssociationCreationError,
    AttributeCreationError,
    AttributeDeleteError,
    AttributeGetError,
    PatentAttributeAssociationCreationError,
)

logger = logger.get_logger(__name__)


class AttributeService(BaseService[AttributeModel, AttributeRepository]):
    """Attribute use cases: attributes and their patent/analog links."""

    repository_type = AttributeRepository

    def __init__(self, session: AsyncSession, **kwargs):
        super().__init__(session=session, **kwargs)
        self._patent_attributes = PatentAttributeRepository(session=session)
        self._analog_attributes = AnalogAttributeRepository(session=session)

    async def create_attributes(self, attributes: list[Attribute]) -> list[Attribute]:
        # Domain `type` is `attribute_type` on the model, so map explicitly.
        with self.raise_as(AttributeCreationError, "Failed to create attributes"):
            models = await self.create_many(await AttributesMapper.to_model(attributes))
        return await AttributesMapper.to_domain(list(models))

    async def create_patent_attribute_associations(
        self, associations: list[PatentAttributeIDPair]
    ) -> None:
        with self.raise_as(
            PatentAttributeAssociationCreationError, "Failed to link attributes to patent"
        ):
            await self._patent_attributes.add_many(
                [
                    PatentAttributeModel(patent_id=a.patent_id, attribute_id=a.attribute_id)
                    for a in associations
                ]
            )

    async def create_analog_attributes(
        self, analog_attributes: dict[int, list[Attribute]]
    ) -> list[Attribute]:
        """Create ANALOG attributes and link each one to its analog."""
        pairs = [
            (analog_id, attribute)
            for analog_id, attributes in analog_attributes.items()
            for attribute in attributes
        ]
        for _, attribute in pairs:
            attribute.type = AttributeType.ANALOG
        saved = await self.create_attributes([attribute for _, attribute in pairs])

        with self.raise_as(
            AnalogAttributeAssociationCreationError, "Failed to link attributes to analogs"
        ):
            await self._analog_attributes.add_many(
                [
                    AnalogAttributeModel(analog_id=analog_id, attribute_id=attribute.id)
                    for (analog_id, _), attribute in zip(pairs, saved, strict=True)
                ]
            )
        return saved

    async def get_patent_attributes(self, patent_id: int) -> list[Attribute]:
        with self.raise_as(AttributeGetError, f"Failed to get attributes for patent {patent_id}"):
            models = await self.repository.list_patent_attributes(patent_id)
        return await self._to_domain(models)

    async def get_matching_analog_attributes(self, patent_id: int) -> list[Attribute]:
        return await self._get_by_type(patent_id, AttributeType.MATCHING_ANALOG)

    async def get_combined_attributes(self, patent_id: int) -> list[Attribute]:
        return await self._get_by_type(patent_id, AttributeType.COMBINED)

    async def get_analog_attribute_rows(
        self, patent_id: int
    ) -> Sequence[tuple[int, str, AttributeModel]]:
        with self.raise_as(
            AttributeGetError, f"Failed to get analog attributes for patent {patent_id}"
        ):
            return await self.repository.list_analog_attribute_rows(patent_id)

    async def get_analog_attributes_grouped(self, patent_id: int) -> list[AnalogAttributesGroupDto]:
        groups = defaultdict(list)
        for analog_id, analog_title, model in await self.get_analog_attribute_rows(patent_id):
            groups[(analog_id, analog_title)].append(await AttributeMapper.to_domain(model))
        return [
            AnalogAttributesGroupDto(
                analog_info=IdNameAnalogDto(id=analog_id, title=title),
                attributes=attributes,
            )
            for (analog_id, title), attributes in groups.items()
        ]

    async def delete_analog_attributes(
        self, patent_id: int, analog_ids: Sequence[int] | None = None
    ) -> None:
        """Delete the ANALOG attributes of the patent's analogs (only ``analog_ids`` if given)."""
        with self.raise_as(
            AttributeDeleteError, f"Failed to delete analog attributes for patent {patent_id}"
        ):
            deleted = await self.repository.delete_analog_attributes_by_patent(
                patent_id, analog_ids
            )
        logger.debug(f"Deleted {deleted} ANALOG attributes for patent {patent_id}")

    async def delete_patent_attributes(self, patent_id: int, attribute_type: AttributeType) -> None:
        with self.raise_as(
            AttributeDeleteError,
            f"Failed to delete {attribute_type} attributes for patent {patent_id}",
        ):
            deleted = await self.repository.delete_by_patent_and_type(patent_id, attribute_type)
        logger.debug(f"Deleted {deleted} {attribute_type} attributes for patent {patent_id}")

    async def _get_by_type(self, patent_id: int, attribute_type: AttributeType) -> list[Attribute]:
        with self.raise_as(
            AttributeGetError,
            f"Failed to get {attribute_type} attributes for patent {patent_id}",
        ):
            models = await self.repository.list_by_patent_and_type(patent_id, attribute_type)
        return await self._to_domain(models)

    @staticmethod
    async def _to_domain(models: Sequence[AttributeModel]) -> list[Attribute]:
        return [await AttributeMapper.to_domain(model) for model in models]
