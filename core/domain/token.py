from dataclasses import dataclass
from datetime import UTC, datetime

from core.enum.token_type import TokenType


@dataclass
class Token:
    jti: str  # Уникальный идентификатор токена (UUID)
    token: str  # Полный JWT токен
    token_type: TokenType  # Тип токена (access/refresh)
    issued_at: datetime  # Время выпуска
    expires_at: datetime  # Время истечения
    revoked: bool = False  # Флаг отзыва
    revoked_at: datetime | None = None  # Время отзыва
    revocation_reason: str | None = None  # Причина отзыва
    last_used_at: datetime | None = None  # Время последнего использования
    user_agent: str | None = None  # User-Agent клиента
    ip_address: str | None = None  # IP-адрес клиента
    device_info: str | None = None  # Информация об устройстве (JSON)

    def update_last_used(self) -> None:
        """Обновляет время последнего использования токена."""
        self.last_used_at = datetime.now(UTC)
