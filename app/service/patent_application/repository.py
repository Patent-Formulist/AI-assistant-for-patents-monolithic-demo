from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from core.db.models.patent_application import PatentApplicationModel


class PatentApplicationRepository(SQLAlchemyAsyncRepository[PatentApplicationModel]):
    model_type = PatentApplicationModel

    async def get_by_patent(self, patent_id: int) -> PatentApplicationModel | None:
        return await self.get_one_or_none(PatentApplicationModel.patent_id == patent_id)
