from core.data_mapper.mapper import StaticMapper
from core.db.models.key_usage import KeyUsageModel
from core.domain.key_usage import KeyUsage


class KeyUsageMapper(StaticMapper[KeyUsage, KeyUsageModel, None]):
    @staticmethod
    async def to_model(key_usage: KeyUsage) -> KeyUsageModel:
        """Convert domain Key usage to DB KeyModel"""
        key_usage_model = KeyUsageModel()

        if key_usage.id is not None:
            key_usage_model.id = key_usage.id

        key_usage_model.key_id = key_usage.key_id
        key_usage_model.created_at = key_usage.created_at
        key_usage_model.limit = key_usage.limit
        key_usage_model.reset_time = key_usage.reset_time
        key_usage_model.used = key_usage.used

        if key_usage.created_at:
            key_usage_model.created_at = key_usage.created_at
        if key_usage.updated_at:
            key_usage_model.updated_at = key_usage.updated_at
        if key_usage.deleted_at:
            key_usage_model.deleted_at = key_usage.deleted_at

        key_usage_model.is_active = key_usage.deleted_at is None

        return key_usage_model

    @staticmethod
    async def to_domain(key_usage_model: KeyUsageModel) -> KeyUsage:
        """Convert DB KeyModel to domain Key"""

        return KeyUsage(
            id=key_usage_model.id,
            key_id=key_usage_model.key_id,
            reset_time=key_usage_model.reset_time,
            used=key_usage_model.used,
            limit=key_usage_model.limit,
            created_at=key_usage_model.created_at,
            updated_at=key_usage_model.updated_at,
            deleted_at=key_usage_model.deleted_at,
        )
