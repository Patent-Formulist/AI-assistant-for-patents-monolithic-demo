from core.data_mapper.mapper import StaticMapper
from core.db.models.analog_attributes import AnalogAttributeModel
from core.domain.analog_attribute import AnalogAttributeIDPair


class AnalogAttributeIdMapper(StaticMapper[AnalogAttributeIDPair, AnalogAttributeModel, None]):
    @staticmethod
    def to_model(analog_attribute: AnalogAttributeIDPair) -> AnalogAttributeModel:
        aam = AnalogAttributeModel()
        aam.analog_id = analog_attribute.analog_id
        aam.attribute_id = analog_attribute.attribute_id
        return aam

    @staticmethod
    def to_domain(analog_attribute: AnalogAttributeModel) -> AnalogAttributeIDPair:
        return AnalogAttributeIDPair(
            analog_id=analog_attribute.analog_id,
            attribute_id=analog_attribute.attribute_id,
        )
