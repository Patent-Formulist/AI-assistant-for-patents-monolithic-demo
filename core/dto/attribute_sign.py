from dataclasses import dataclass, field


@dataclass
class AttributeSignDetailDto:
    attr_id: int
    attr_title: str
    sign: bool


@dataclass
class PatentAttributesSignDto:
    attributes: dict[int, AttributeSignDetailDto] = field(default_factory=dict)


@dataclass
class AnalogSignsDto:
    analog_id: int
    analog_num: str
    attributes: dict[int, AttributeSignDetailDto] = field(default_factory=dict)


AnalogSignsMap = dict[int, AnalogSignsDto]
