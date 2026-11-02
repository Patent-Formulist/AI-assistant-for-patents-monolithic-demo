from sqlalchemy import BigInteger, Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from sqlalchemy.orm import relationship, validates

from core.db.db import Base
from core.db.mixins import SoftDeleteMixin, TimestampMixin
from core.enum.user_status import UserStatus


class UserModel(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    # Основной идентификатор
    id = Column(
        BigInteger,
        primary_key=True,
        index=True,
        autoincrement=True,
        comment="Автоинкрементный ID пользователя",
    )

    # Учетные данные
    tg_id = Column(String(20), unique=True, index=True, nullable=True, comment="tg_id")
    email = Column(
        String(255),
        unique=True,
        index=True,
        nullable=True,
        comment="Уникальный email пользователя (макс. 255 символов)",
    )
    username = Column(
        String(50),
        unique=True,
        index=True,
        nullable=True,
        comment="Уникальное имя пользователя (опционально)",
    )
    hashed_password = Column(
        String(255), nullable=True, comment="Хеш пароля (bcrypt/scrypt/argon2)"
    )

    # Информация о пользователе
    first_name = Column(String(100), nullable=True, comment="Имя")
    last_name = Column(String(100), nullable=True, comment="Фамилия")
    avatar_url = Column(Text, nullable=True, comment="URL аватара")
    bio = Column(Text, nullable=True, comment="О себе")

    # Статус и верификация
    status = Column(
        PGEnum(UserStatus, name="user_status"),
        default=UserStatus.PENDING,
        nullable=False,
        comment="Статус аккаунта",
    )
    is_admin = Column(
        Boolean, default=False, server_default="false", nullable=False, comment="Администратор"
    )
    is_email_verified = Column(Boolean, default=False, comment="Подтвержден ли email")
    email_verified_at = Column(DateTime, nullable=True, comment="Время подтверждения email")
    email_verification_sent_at = Column(
        DateTime, nullable=True, comment="Когда отправлено последнее письмо подтверждения"
    )

    # Защита от bruteforce
    failed_login_attempts = Column(Integer, default=0, comment="Количество неудачных попыток входа")
    locked_until = Column(DateTime, nullable=True, comment="Время до разблокировки аккаунта")
    last_failed_login = Column(DateTime, nullable=True, comment="Время последней неудачной попытки")

    # Аудит
    last_login_at = Column(DateTime, nullable=True, comment="Время последнего успешного входа")
    last_login_ip = Column(
        String(45), nullable=True, comment="IP последнего входа (поддержка IPv6)"
    )
    last_activity_at = Column(DateTime, nullable=True, comment="Время последней активности")

    # Связи
    user_tokens = relationship(
        "UserTokenModel", back_populates="user", cascade="all, delete-orphan"
    )
    user_patents = relationship("UserPatentModel", back_populates="user")

    @validates("email")
    def validate_email(self, key, email):
        """Базовая валидация email"""
        if "@" not in email:
            raise ValueError("Invalid email format")
        return email

    @property
    def is_active(self):
        """Проверка, активен ли пользователь (для аутентификации)"""
        return self.status == UserStatus.ACTIVE

    @property
    def full_name(self):
        """Полное имя пользователя"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username or self.email.split("@")[0]
