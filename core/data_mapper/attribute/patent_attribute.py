from core.data_mapper.mapper import StaticMapper
from core.db.models.patent_attributes import PatentAttributeModel
from core.domain.patent_attribute import PatentAttributeIDPair


class PatentAttributeIdMapper(StaticMapper[PatentAttributeIDPair, PatentAttributeModel, None]):
    @staticmethod
    async def to_model(patent_attribute: PatentAttributeIDPair) -> PatentAttributeModel:
        pam = PatentAttributeModel()
        pam.patent_id = patent_attribute.patent_id
        pam.attribute_id = patent_attribute.attribute_id
        return pam

    @staticmethod
    async def to_domain(
        patent_attribute: PatentAttributeModel,
    ) -> PatentAttributeIDPair:
        return PatentAttributeIDPair(
            patent_id=patent_attribute.patent_id,
            attribute_id=patent_attribute.attribute_id,
        )
