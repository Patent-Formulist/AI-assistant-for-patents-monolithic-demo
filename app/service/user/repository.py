from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from core.db.models.user import UserModel


class UserRepository(SQLAlchemyAsyncRepository[UserModel]):
    model_type = UserModel
