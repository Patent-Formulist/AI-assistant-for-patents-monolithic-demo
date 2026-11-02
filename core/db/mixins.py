from sqlalchemy import BigInteger, Boolean, Column, DateTime
from sqlalchemy.sql import func


class SoftDeleteMixin:
    """Mixin for gentle removal"""

    is_active = Column(Boolean, default=True, nullable=False, index=True)
    deleted_at = Column(DateTime, nullable=True)
    deleted_by = Column(BigInteger, nullable=True)


class TimestampMixin:
    """Mixin for timestamps"""

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
