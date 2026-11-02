from dataclasses import dataclass


@dataclass
class IdentifyRowDto:
    general_attr_id: int | None = None
    general_attr_title: str | None = None
    patent_attr_id: int | None = None
    patent_attr_title: str | None = None
    analog_attr_id: int | None = None
    analog_attr_title: str | None = None


@dataclass
class IdentifyPrototypeDto:
    analog_id: int
    analog_num: str
    row: list[IdentifyRowDto]
    new_analog_attribute: dict[int, str] | None = None
