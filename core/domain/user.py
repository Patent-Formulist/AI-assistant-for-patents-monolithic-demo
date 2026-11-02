from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    user_id: int | None = None
    tg_id: str | None = None
    email: str | None = None
    username: str | None = None
    hashed_password: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
    status: str = "PENDING"
    is_email_verified: bool = False
    email_verified_at: datetime | None = None
    failed_login_attempts: int = 0
    locked_until: datetime | None = None
    last_failed_login: datetime | None = None
    last_login_at: datetime | None = None
    last_login_ip: str | None = None
    last_activity_at: datetime | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self):
        if not self.user_id:
            raise ValueError("User user_id not valid")
