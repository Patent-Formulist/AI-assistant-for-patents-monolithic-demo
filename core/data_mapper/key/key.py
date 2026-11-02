from core.data_mapper.mapper import StaticMapper
from core.db.models.key import KeyModel
from core.domain.key import Key


class KeyMapper(StaticMapper[Key, KeyModel, None]):
    @staticmethod
    async def to_model(key: Key) -> KeyModel:
        """Convert domain Key to DB KeyModel"""
        key_model = KeyModel()

        if key.id is not None:
            key_model.id = key.id

        key_model.key = key.key
        key_model.key_type = key.key_type
        key_model.revoked = key.revoked
        key_model.revocation_reason = key.revocation_reason
        key_model.revoked_at = key.revoked_at
        key_model.issued_at = key.issued_at
        key_model.expires_at = key.expires_at
        key_model.last_used_at = key.last_used_at

        if key.created_at:
            key_model.created_at = key.created_at
        if key.updated_at:
            key_model.updated_at = key.updated_at
        if key.deleted_at:
            key_model.deleted_at = key.deleted_at

        key_model.is_active = key.deleted_at is None

        return key_model

    @staticmethod
    async def to_domain(key_model: KeyModel) -> Key:
        """Convert DB KeyModel to domain Key"""

        return Key(
            id=key_model.id,
            key=key_model.key,
            key_type=key_model.key_type,
            expires_at=key_model.expires_at,
            revoked=key_model.revoked or False,
            revocation_reason=key_model.revocation_reason,
            revoked_at=key_model.revoked_at,
            issued_at=key_model.issued_at,
            last_used_at=key_model.last_used_at,
            created_at=key_model.created_at,
            updated_at=key_model.updated_at,
            deleted_at=key_model.deleted_at,
        )
