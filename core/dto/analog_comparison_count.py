from dataclasses import dataclass


@dataclass
class AnalogComparisonCount:
    """Количество совпадений для одного аналога."""

    analog_id: int
    count: int
