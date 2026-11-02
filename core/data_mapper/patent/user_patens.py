from core.data_mapper.mapper import StaticMapper
from core.db.models.user_patents import UserPatentModel
from core.domain.user_patent import UserPatentIDPair


class UserPatentIdMapper(StaticMapper[UserPatentIDPair, UserPatentModel, None]):
    @staticmethod
    async def to_model(user_patent: UserPatentIDPair) -> UserPatentModel:
        upm = UserPatentModel()
        upm.user_id = user_patent.user_id
        upm.patent_id = user_patent.patent_id
        return upm

    @staticmethod
    async def to_domain(user_patents: UserPatentModel) -> UserPatentIDPair:
        return UserPatentIDPair(user_id=user_patents.user_id, patent_id=user_patents.patent_id)
