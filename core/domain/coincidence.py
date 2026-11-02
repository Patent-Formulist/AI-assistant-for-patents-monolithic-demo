from dataclasses import dataclass


@dataclass
class Coincidence:
    patent_id: int
    analog_id: int
    coincidence: int

    def __post_init__(self):
        """Валидация после инициализации"""
        if not isinstance(self.patent_id, int) or self.patent_id <= 0:
            raise ValueError("patent_id must be a positive integer")
        if not isinstance(self.analog_id, int) or self.analog_id <= 0:
            raise ValueError("analog_id must be a positive integer")
        if not isinstance(self.coincidence, int) or self.coincidence < 0:
            raise ValueError("coincidence must be a non-negative integer")
