from datetime import UTC, datetime

from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from uuid6 import uuid7

from core.db.db import Base
from core.db.mixins import SoftDeleteMixin, TimestampMixin
from core.db.types import GUID
from core.enum.token_key import KeyType


class KeyModel(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "key"

    id = Column(
        GUID(),
        primary_key=True,
        default=lambda: str(uuid7()),
        comment="Уникальный идентификатор uuid7",
    )
    key = Column(Text, nullable=False, unique=True, comment="Ключ")
    key_type = Column(PGEnum(KeyType, name="key_type"), nullable=False, comment="Тип ключа")
    revoked = Column(Boolean, default=False, comment="Отозван ли ключ")
    revocation_reason = Column(String(100), nullable=True, comment="Причина отзыва")
    revoked_at = Column(DateTime(timezone=True), nullable=True, comment="Время отзыва")

    issued_at = Column(DateTime(timezone=True), server_default=func.now(), comment="Время выдачи")
    expires_at = Column(DateTime(timezone=True), nullable=False, comment="Время истечения")
    last_used_at = Column(
        DateTime(timezone=True), nullable=True, comment="Время последнего использования"
    )

    usages = relationship("KeyUsageModel", back_populates="key", cascade="all, delete-orphan")

    @property
    def is_expired(self):
        return datetime.now(UTC) > self.expires_at

    @property
    def is_valid(self):
        return not self.revoked and not self.is_expired
