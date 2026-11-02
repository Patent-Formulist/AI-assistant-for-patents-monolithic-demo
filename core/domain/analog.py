from dataclasses import dataclass
from datetime import datetime


@dataclass
class Analog:
    title: str
    analog_num: str
    analog_link: str
    id: int = None
    abstract: str = ""
    claims: str = ""
    description: str = ""
    # None: set by the DB on create, left untouched by BaseService.update.
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self):
        """Валидация после инициализации"""
        if not self.title or not self.title.strip():
            raise ValueError("The analog title cannot be empty")

        if not self.analog_num or not self.analog_num.strip():
            raise ValueError("The analog number cannot be empty")

        if not self.analog_link or not self.analog_link.strip():
            raise ValueError("The analog link cannot be empty")

    def __str__(self) -> str:
        """Строковое представление объекта"""
        return (
            f"Analog({self.analog_num}: {self.title[:50]}{'...' if len(self.title) > 50 else ''})"
        )
