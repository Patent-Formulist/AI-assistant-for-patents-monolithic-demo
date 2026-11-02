from collections.abc import Sequence

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import select

from core.db.models.patent import PatentModel
from core.db.models.user_patents import UserPatentModel


class PatentRepository(SQLAlchemyAsyncRepository[PatentModel]):
    model_type = PatentModel

    async def list_by_user(self, user_id: int) -> Sequence[PatentModel]:
        return await self.list(
            statement=select(PatentModel)
            .join(PatentModel.user_patents)
            .where(
                UserPatentModel.user_id == user_id,
                UserPatentModel.is_active,
                PatentModel.is_active,
            )
        )


class UserPatentRepository(SQLAlchemyAsyncRepository[UserPatentModel]):
    model_type = UserPatentModel
