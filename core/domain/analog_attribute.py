from dataclasses import dataclass


@dataclass
class AnalogAttributeIDPair:
    attribute_id: int
    analog_id: int
    id: int | None = None
