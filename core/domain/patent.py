from dataclasses import dataclass
from datetime import datetime


@dataclass
class Patent:
    name: str
    id: int
    search_query: str = ""
    appointment: str = ""
    construction: str = ""
    operation_principle: str = ""
    technical_area: str = ""
    technical_result: str = ""
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self):
        if not self.name:
            raise ValueError("Patent name not valid")
