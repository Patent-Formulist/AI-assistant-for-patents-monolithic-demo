from enum import Enum


class UserStatus(str, Enum):
    PENDING = "pending"  # Ожидает подтверждения email
    ACTIVE = "active"  # Активный
    SUSPENDED = "suspended"  # Временная блокировка
    BANNED = "banned"  # Перманентная блокировка
