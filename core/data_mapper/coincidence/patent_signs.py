from core.data_mapper.mapper import StaticMapper
from core.db.models.patent_attribute_sign import PatentAttributeSignModel
from core.domain.patent_sign import PatentAttributeSign


class PatentAttributeSignsMapper(
    StaticMapper[list[PatentAttributeSign], list[PatentAttributeSignModel], None]
):
    @staticmethod
    def to_model(
        patent_attributes: list[PatentAttributeSign],
    ) -> list[PatentAttributeSignModel]:
        models = []
        for attr in patent_attributes:
            pas = PatentAttributeSignModel()
            pas.patent_id = attr.patent_id
            pas.attribute_id = attr.attribute_id
            pas.sign = attr.sign
            models.append(pas)
        return models

    @staticmethod
    def to_domain(
        patent_attributes: list[PatentAttributeSignModel],
    ) -> list[PatentAttributeSign]:
        domains = []
        for model in patent_attributes:
            domains.append(
                PatentAttributeSign(
                    patent_id=model.patent_id,
                    attribute_id=model.attribute_id,
                    sign=model.sign,
                )
            )
        return domains
