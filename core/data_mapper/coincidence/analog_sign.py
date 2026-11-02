from core.data_mapper.mapper import StaticMapper
from core.db.models.analog_attribute_sign import AnalogAttributeSignModel
from core.domain.analog_sign import AnalogAttributeSign


class AnalogAttributeSignMapper(StaticMapper[AnalogAttributeSign, AnalogAttributeSignModel, None]):
    @staticmethod
    async def to_model(
        analog_attribute: AnalogAttributeSign,
    ) -> AnalogAttributeSignModel:
        aas = AnalogAttributeSignModel()
        aas.analog_id = analog_attribute.analog_id
        aas.attribute_id = analog_attribute.attribute_id
        aas.sign = analog_attribute.sign
        return aas

    @staticmethod
    async def to_domain(
        analog_attribute: AnalogAttributeSignModel,
    ) -> AnalogAttributeSign:
        return AnalogAttributeSign(
            analog_id=analog_attribute.analog_id,
            attribute_id=analog_attribute.attribute_id,
            sign=analog_attribute.sign,
        )
