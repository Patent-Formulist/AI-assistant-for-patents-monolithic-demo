from dataclasses import dataclass


@dataclass
class AnalogAttributeSign:
    attribute_id: int
    analog_id: int
    sign: bool | None = None
