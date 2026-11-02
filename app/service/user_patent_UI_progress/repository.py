from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from core.db.models.user_patents import UserPatentModel


class UserPatentRepository(SQLAlchemyAsyncRepository[UserPatentModel]):
    model_type = UserPatentModel
