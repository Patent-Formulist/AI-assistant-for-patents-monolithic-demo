from core.data_mapper.mapper import StaticMapper
from core.db.models.token import TokenModel
from core.domain.token import Token
from core.enum.token_type import TokenType


class TokenMapper(StaticMapper[Token, TokenModel, None]):
    @staticmethod
    async def to_model(token: Token) -> TokenModel:
        """Convert domain Token to DB TokenModel"""
        token_model = TokenModel()

        token_model.jti = token.jti
        token_model.token = token.token
        token_model.token_type = token.token_type.value
        token_model.issued_at = token.issued_at
        token_model.expires_at = token.expires_at

        token_model.revoked = token.revoked
        if token.revoked_at is not None:
            token_model.revoked_at = token.revoked_at
        if token.revocation_reason is not None:
            token_model.revocation_reason = token.revocation_reason
        if token.last_used_at is not None:
            token_model.last_used_at = token.last_used_at
        if token.user_agent is not None:
            token_model.user_agent = token.user_agent
        if token.ip_address is not None:
            token_model.ip_address = token.ip_address
        if token.device_info is not None:
            token_model.device_info = token.device_info

        return token_model

    @staticmethod
    async def to_domain(token_model: TokenModel) -> Token:
        """Convert DB TokenModel to domain Token"""
        return Token(
            jti=token_model.jti,
            token=token_model.token,
            token_type=TokenType(token_model.token_type),
            issued_at=token_model.issued_at,
            expires_at=token_model.expires_at,
            revoked=token_model.revoked,
            revoked_at=token_model.revoked_at,
            revocation_reason=token_model.revocation_reason,
            last_used_at=token_model.last_used_at,
            user_agent=token_model.user_agent,
            ip_address=token_model.ip_address,
            device_info=token_model.device_info,
        )
