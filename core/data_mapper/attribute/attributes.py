from datetime import datetime

from core.data_mapper.mapper import StaticMapper
from core.db.models.attribute import AttributeModel
from core.domain.attribute import Attribute


class AttributesMapper(StaticMapper[list[Attribute], list[AttributeModel], None]):
    @staticmethod
    async def to_model(attributes: list[Attribute]) -> list[AttributeModel]:
        """Convert domain Attribute to DB AttributeModel"""
        attribute_models = []
        for attribute in attributes:
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

            attribute_models.append(attribute_model)
        return attribute_models

    @staticmethod
    async def to_domain(attribute_models: list[AttributeModel]) -> list[Attribute]:
        """Convert DB AttributeModel to domain Attribute"""
        attribute_domain = []
        for attribute_model in attribute_models:
            attr = Attribute(
                id=attribute_model.id,
                name=attribute_model.name,
                type=attribute_model.attribute_type,
                created_at=attribute_model.created_at or datetime.now(),
                updated_at=attribute_model.updated_at or datetime.now(),
            )
            attribute_domain.append(attr)
        return attribute_domain
