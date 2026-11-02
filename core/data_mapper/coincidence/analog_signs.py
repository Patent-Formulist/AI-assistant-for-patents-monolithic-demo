from core.data_mapper.mapper import StaticMapper
from core.db.models.analog_attribute_sign import AnalogAttributeSignModel
from core.domain.analog_sign import AnalogAttributeSign


class AnalogAttributeSignsMapper(
    StaticMapper[list[AnalogAttributeSign], list[AnalogAttributeSignModel], None]
):
    @staticmethod
    def to_model(
        analog_attributes: list[AnalogAttributeSign],
    ) -> list[AnalogAttributeSignModel]:
        models = []
        for attr in analog_attributes:
            aas = AnalogAttributeSignModel()
            aas.analog_id = attr.analog_id
            aas.attribute_id = attr.attribute_id
            aas.sign = attr.sign
            models.append(aas)
        return models

    @staticmethod
    def to_domain(
        analog_attributes: list[AnalogAttributeSignModel],
    ) -> list[AnalogAttributeSign]:
        domains = []
        for model in analog_attributes:
            domains.append(
                AnalogAttributeSign(
                    analog_id=model.analog_id,
                    attribute_id=model.attribute_id,
                    sign=model.sign,
                )
            )
        return domains
