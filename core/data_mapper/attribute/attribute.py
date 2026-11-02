from datetime import datetime

from core.data_mapper.mapper import StaticMapper
from core.db.models.attribute import AttributeModel
from core.domain.attribute import Attribute


class AttributeMapper(StaticMapper[Attribute, AttributeModel, None]):
    @staticmethod
    async def to_model(attribute: Attribute) -> AttributeModel:
        """Convert domain Attribute to DB AttributeModel"""
        attribute_model = AttributeModel()
        if attribute.id is not None:
            attribute_model.id = attribute.id
        if attribute.name is not None:
            attribute_model.name = attribute.name
        if attribute.type is not None:
            attribute_model.attribute_type = attribute.type

        if attribute.created_at:
            attribute_model.created_at = attribute.created_at
        if attribute.updated_at:
            attribute_model.updated_at = attribute.updated_at

        return attribute_model

    @staticmethod
    async def to_domain(attribute_model: AttributeModel) -> Attribute:
        """Convert DB AttributeModel to domain Attribute"""
        return Attribute(
            id=attribute_model.id,
            name=attribute_model.name,
            type=attribute_model.attribute_type,
            created_at=attribute_model.created_at or datetime.now(),
            updated_at=attribute_model.updated_at or datetime.now(),
        )
