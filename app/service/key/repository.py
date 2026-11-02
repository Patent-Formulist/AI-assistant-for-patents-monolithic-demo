from datetime import timedelta

from advanced_alchemy.repository import SQLAlchemyAsyncRepository
from sqlalchemy import and_, case, func, or_, select, update

from core.db.models.key import KeyModel
from core.db.models.key_usage import KeyUsageModel
from core.enum.token_key import KeyType

# Cooldown after a key reaches its usage limit
KEY_COOLDOWN = timedelta(seconds=30)


class KeyRepository(SQLAlchemyAsyncRepository[KeyModel]):
    model_type = KeyModel


class KeyUsageRepository(SQLAlchemyAsyncRepository[KeyUsageModel]):
    model_type = KeyUsageModel

    async def take_usage(self, key_type: KeyType) -> str | None:
        """Atomically count one use of the least used available key; return its key_id.

        One UPDATE picks the key and increments the counter. The limit and
        cooldown conditions are repeated in the UPDATE's own WHERE, so a
        concurrent transaction that waited on the row lock re-checks them on
        the latest row version (and gets no row) instead of overwriting the
        counter. Returns None when no key is available right now.
        """
        usage, key = KeyUsageModel, KeyModel
        now = func.now()
        cooldown_over = and_(usage.reset_time.is_not(None), usage.reset_time <= now)
        usable = or_(and_(usage.reset_time.is_(None), usage.used < usage.limit), cooldown_over)
        # SET expressions see the old row, so both use the same new counter value
        new_used = case((cooldown_over, 1), else_=usage.used + 1)

        candidate = (
            select(usage.id)
            .join(key, key.id == usage.key_id)
            .where(
                key.key_type == key_type,
                key.revoked.is_(False),
                key.expires_at > now,
                usable,
            )
            .order_by(case((cooldown_over, 0), else_=usage.used), usage.id)
            .limit(1)
            .scalar_subquery()
        )
        result = await self.session.execute(
            update(usage)
            .where(usage.id == candidate, usable)
            .values(
                used=new_used,
                reset_time=case((new_used >= usage.limit, now + KEY_COOLDOWN), else_=None),
            )
            .returning(usage.key_id)
            .execution_options(synchronize_session=False)
        )
        return result.scalar_one_or_none()
