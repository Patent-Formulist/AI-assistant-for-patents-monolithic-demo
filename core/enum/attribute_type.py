from enum import Enum


class AttributeType(str, Enum):
    ANALOG = "analog"
    PATENT = "patent"
    MATCHING_ANALOG = "matching_analog"
    COMBINED = "combined"
    IDENTIFIER = "identifier"
