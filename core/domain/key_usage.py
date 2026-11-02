from dataclasses import dataclass
from datetime import datetime


@dataclass
class KeyUsage:
    key_id: str

    id: str | None = None
    used: int | None = 0
    limit: int | None = 5
    reset_time: datetime | None = None

    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
