from dataclasses import dataclass
from datetime import UTC, datetime

from core.enum.token_key import KeyType


@dataclass
class Key:
    """Доменная модель ключа API"""

    key: str
    key_type: KeyType
    expires_at: datetime

    id: str | None = None
    revoked: bool = False
    revocation_reason: str | None = None
    revoked_at: datetime | None = None
    issued_at: datetime | None = None
    last_used_at: datetime | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None

    def __post_init__(self):
        """Валидация после инициализации"""
        self._validate_required_fields()
        self._validate_dates()

        if self.issued_at is None:
            self.issued_at = datetime.now()

    def _validate_required_fields(self):
        """Проверка обязательных полей"""
        if not self.key or not self.key.strip():
            raise ValueError("Key cannot be empty")

        if not self.key_type:
            raise ValueError("Key type must be specified")

        if not self.expires_at:
            raise ValueError("Expiration date must be specified")

    def _validate_dates(self):
        """Проверка корректности дат"""
        now = datetime.now(UTC)

        if self.expires_at <= now:
            raise ValueError("Expiration date must be in the future")

        if self.revoked_at and self.revoked_at > now:
            raise ValueError("Revocation date cannot be in the future")

        if self.issued_at and self.issued_at > now:
            raise ValueError("Issue date cannot be in the future")

    @property
    def is_expired(self) -> bool:
        """Проверка, истёк ли срок действия ключа"""
        return datetime.now() > self.expires_at

    @property
    def is_valid(self) -> bool:
        """Проверка валидности ключа (не отозван и не истёк)"""
        return not self.revoked and not self.is_expired

    @property
    def days_until_expiry(self) -> int:
        """Количество дней до истечения срока"""
        if self.is_expired:
            return 0
        delta = self.expires_at - datetime.now()
        return delta.days

    def revoke(self, reason: str | None = None) -> None:
        """Отзыв ключа"""
        if self.revoked:
            raise ValueError("Key is already revoked")

        self.revoked = True
        self.revoked_at = datetime.now()
        self.revocation_reason = reason

    def use(self) -> None:
        """Отметить использование ключа"""
        self.last_used_at = datetime.now()

    def extend_expiry(self, days: int) -> None:
        """Продлить срок действия ключа"""
        if days <= 0:
            raise ValueError("Days must be positive")

        new_expiry = self.expires_at.replace(
            year=self.expires_at.year,
            month=self.expires_at.month,
            day=self.expires_at.day + days,
        )

        # Проверяем, что новое время истечения не раньше текущего
        if new_expiry <= datetime.now():
            raise ValueError("Extended expiry must be in the future")

        self.expires_at = new_expiry
