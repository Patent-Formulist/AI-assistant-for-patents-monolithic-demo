from enum import Enum


class AIPurpose(Enum):
    ANALOG_ATTRIBUTE_GENERATION = "analog_attribute_generation"
    PATENT_ATTRIBUTE_GENERATION = "pattern_attribute_generation"
    ANALOG_ATTRIBUTE_MATCHER = "analog_attribute_matcher"
    PATENT_ATTRIBUTE_MATCHER = "patent_attribute_matcher"
    GENERAL_ATTRIBUTE = "general_attribute"
    ANALOG_CHECKING_ATTRIBUTE = "analog_checking_attribute"
    PATENT_CHECKING_ATTRIBUTE = "patent_checking_attribute"
    IDENTIFY = "identify"
