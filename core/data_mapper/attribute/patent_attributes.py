from core.data_mapper.mapper import StaticMapper
from core.db.models.patent_attributes import PatentAttributeModel
from core.domain.patent_attribute import PatentAttributeIDPair


class PatentAttributesIdMapper(
    StaticMapper[list[PatentAttributeIDPair], list[PatentAttributeModel], None]
):
    @staticmethod
    async def to_model(
        patent_attributes: list[PatentAttributeIDPair],
    ) -> list[PatentAttributeModel]:
        patent_attribute_models = []
        for patent_attribute in patent_attributes:
            pam = PatentAttributeModel()
            pam.patent_id = patent_attribute.patent_id
            pam.attribute_id = patent_attribute.attribute_id
            patent_attribute_models.append(pam)
        return patent_attribute_models

    @staticmethod
    async def to_domain(
        patent_attributes: list[PatentAttributeModel],
    ) -> list[PatentAttributeIDPair]:
        patent_attribute_domains = []
        for patent_attribute in patent_attributes:
            pad = PatentAttributeIDPair(
                patent_id=patent_attribute.patent_id,
                attribute_id=patent_attribute.attribute_id,
            )
            patent_attribute_domains.append(pad)
        return patent_attribute_domains
