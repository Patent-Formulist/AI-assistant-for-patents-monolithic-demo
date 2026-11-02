from core.data_mapper.mapper import StaticMapper
from core.db.models.analog_attributes import AnalogAttributeModel
from core.domain.analog_attribute import AnalogAttributeIDPair


class AnalogAttributesIdMapper(
    StaticMapper[list[AnalogAttributeIDPair], list[AnalogAttributeModel], None]
):
    @staticmethod
    def to_model(
        analog_attributes: list[AnalogAttributeIDPair],
    ) -> list[AnalogAttributeModel]:
        analog_attribute_models = []
        for analog_attribute in analog_attributes:
            aam = AnalogAttributeModel()
            aam.analog_id = analog_attribute.analog_id
            aam.attribute_id = analog_attribute.attribute_id
            analog_attribute_models.append(aam)
        return analog_attribute_models

    @staticmethod
    def to_domain(
        analog_attributes: list[AnalogAttributeModel],
    ) -> list[AnalogAttributeIDPair]:
        analog_attribute_domains = []
        for analog_attribute in analog_attributes:
            aad = AnalogAttributeIDPair(
                analog_id=analog_attribute.analog_id,
                attribute_id=analog_attribute.attribute_id,
            )
            analog_attribute_domains.append(aad)
        return analog_attribute_domains
