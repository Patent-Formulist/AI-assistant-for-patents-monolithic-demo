from core.data_mapper.mapper import StaticMapper
from core.db.models.patent_attribute_sign import PatentAttributeSignModel
from core.domain.patent_sign import PatentAttributeSign


class PatentAttributeSignMapper(StaticMapper[PatentAttributeSign, PatentAttributeSignModel, None]):
    @staticmethod
    async def to_model(
        analog_attribute: PatentAttributeSign,
    ) -> PatentAttributeSignModel:
        pas = PatentAttributeSignModel()
        pas.patent_id = analog_attribute.patent_id
        pas.attribute_id = analog_attribute.attribute_id
        pas.sign = analog_attribute.sign
        return pas

    @staticmethod
    async def to_domain(
        analog_attribute: PatentAttributeSignModel,
    ) -> PatentAttributeSign:
        return PatentAttributeSign(
            patent_id=analog_attribute.patent_id,
            attribute_id=analog_attribute.attribute_id,
            sign=analog_attribute.sign,
        )
