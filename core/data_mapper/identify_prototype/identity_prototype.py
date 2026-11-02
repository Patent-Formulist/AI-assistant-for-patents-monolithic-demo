from core.data_mapper.mapper import StaticMapper
from core.db.models.identify_attribute import IdentifyAttributeModel
from core.domain.identify_prototype import IdentityPrototype


class IdentifyAttributeMapper(StaticMapper[IdentityPrototype, IdentifyAttributeModel, None]):
    @staticmethod
    async def to_model(identity_prototype: IdentityPrototype) -> IdentifyAttributeModel:
        identity_prototype_model = IdentifyAttributeModel()
        if identity_prototype.id is not None:
            identity_prototype_model.id = identity_prototype.id
        if identity_prototype.patent_id is not None:
            identity_prototype_model.patent_id = identity_prototype.patent_id
        if identity_prototype.analog_id is not None:
            identity_prototype_model.analog_id = identity_prototype.analog_id

        if identity_prototype.patent_attribute_id is not None:
            identity_prototype_model.patent_attribute_id = identity_prototype.patent_attribute_id
        if identity_prototype.analog_attribute_id is not None:
            identity_prototype_model.analog_attribute_id = identity_prototype.analog_attribute_id
        if identity_prototype.general_attribute_id is not None:
            identity_prototype_model.general_attribute_id = identity_prototype.general_attribute_id

        return identity_prototype_model

    @staticmethod
    async def to_domain(
        identity_prototype: IdentifyAttributeModel,
    ) -> IdentityPrototype:
        return IdentityPrototype(
            id=identity_prototype.id,
            patent_id=identity_prototype.patent_id,
            analog_id=identity_prototype.analog_id,
            patent_attribute_id=identity_prototype.patent_attribute_id,
            general_attribute_id=identity_prototype.general_attribute_id,
            analog_attribute_id=identity_prototype.analog_attribute_id,
        )
