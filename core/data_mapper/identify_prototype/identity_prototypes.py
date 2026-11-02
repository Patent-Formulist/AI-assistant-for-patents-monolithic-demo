from core.data_mapper.mapper import StaticMapper
from core.db.models.identify_attribute import IdentifyAttributeModel
from core.domain.identify_prototype import IdentityPrototype


class IdentifyAttributesMapper(
    StaticMapper[list[IdentityPrototype], list[IdentifyAttributeModel], None]
):
    @staticmethod
    async def to_model(
        identity_prototypes: list[IdentityPrototype],
    ) -> list[IdentifyAttributeModel]:
        identity_prototype_models = []
        for identity_prototype in identity_prototypes:
            identity_prototype_model = IdentifyAttributeModel()
            if identity_prototype.id is not None:
                identity_prototype_model.id = identity_prototype.id
            if identity_prototype.patent_id is not None:
                identity_prototype_model.patent_id = identity_prototype.patent_id
            if identity_prototype.analog_id is not None:
                identity_prototype_model.analog_id = identity_prototype.analog_id

            if identity_prototype.patent_attribute_id is not None:
                identity_prototype_model.patent_attribute_id = (
                    identity_prototype.patent_attribute_id
                )
            if identity_prototype.analog_attribute_id is not None:
                identity_prototype_model.analog_attribute_id = (
                    identity_prototype.analog_attribute_id
                )
            if identity_prototype.general_attribute_id is not None:
                identity_prototype_model.general_attribute_id = (
                    identity_prototype.general_attribute_id
                )
            identity_prototype_models.append(identity_prototype_model)
        return identity_prototype_models

    @staticmethod
    async def to_domain(
        identity_prototypes: list[IdentifyAttributeModel],
    ) -> list[IdentityPrototype]:
        identity_prototype_domains = []
        for identity_prototype in identity_prototypes:
            ip = IdentityPrototype(
                id=identity_prototype.id,
                patent_id=identity_prototype.patent_id,
                analog_id=identity_prototype.analog_id,
                patent_attribute_id=identity_prototype.patent_attribute_id,
                general_attribute_id=identity_prototype.general_attribute_id,
                analog_attribute_id=identity_prototype.analog_attribute_id,
            )
            identity_prototype_domains.append(ip)
        return identity_prototype_domains
