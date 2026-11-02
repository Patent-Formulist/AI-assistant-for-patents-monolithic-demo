from advanced_alchemy.repository import SQLAlchemyAsyncRepository

from core.db.models.token import TokenModel
from core.db.models.user_token import UserTokenModel


class TokenRepository(SQLAlchemyAsyncRepository[TokenModel]):
    model_type = TokenModel
    id_attribute = "jti"


class UserTokenRepository(SQLAlchemyAsyncRepository[UserTokenModel]):
    model_type = UserTokenModel
