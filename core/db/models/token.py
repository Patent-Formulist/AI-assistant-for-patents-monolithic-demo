from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql import func
from uuid6 import uuid7

from core.db.db import Base
from core.db.mixins import SoftDeleteMixin, TimestampMixin
from core.db.types import GUID
from core.enum.token_type import TokenType


class TokenModel(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "tokens"

    jti = Column(
        GUID(),
        primary_key=True,
        default=lambda: str(uuid7()),
        comment="Уникальный идентификатор JWT uuid7",
    )
    token = Column(Text, nullable=False, unique=True, comment="Полный JWT токен")
    token_type = Column(PGEnum(TokenType, name="token_type"), nullable=False, comment="Тип токена")
    revoked = Column(Boolean, default=False, comment="Отозван ли токен")
    revocation_reason = Column(String(100), nullable=True, comment="Причина отзыва")

    # Информация о клиенте
    user_agent = Column(Text, nullable=True, comment="User-Agent клиента")
    ip_address = Column(String(45), nullable=True, comment="IP адрес (поддержка IPv6)")
    device_info = Column(Text, nullable=True, comment="Информация об устройстве (JSON)")

    # Временные метки
    issued_at = Column(DateTime(timezone=True), server_default=func.now(), comment="Время выдачи")
    expires_at = Column(DateTime(timezone=True), nullable=False, comment="Время истечения")
    last_used_at = Column(
        DateTime(timezone=True), nullable=True, comment="Время последнего использования"
    )
    revoked_at = Column(DateTime(timezone=True), nullable=True, comment="Время отзыва")

    # Связи
    user_tokens = relationship(
        "UserTokenModel", back_populates="token", cascade="all, delete-orphan"
    )

    @validates("token_type")
    def validate_token_type(self, key, token_type):
        if token_type not in [t.value for t in TokenType]:
            raise ValueError(f"Invalid token type: {token_type}")
        return token_type
