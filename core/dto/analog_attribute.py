from dataclasses import dataclass, field

from core.domain.attribute import Attribute
from core.dto.id_name_analog import IdNameAnalogDto


@dataclass
class AnalogAttributesGroupDto:
    analog_info: IdNameAnalogDto
    attributes: list[Attribute]


@dataclass
class AnalogAttributeDto:
    analog_info: IdNameAnalogDto
    attribute: Attribute


@dataclass
class AnalogAttributeListDto:
    analog_attribute: list[AnalogAttributeDto] = field(default_factory=list)
