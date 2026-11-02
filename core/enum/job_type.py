import enum


class JobType(str, enum.Enum):
    STATISTICS = "statistics"
    ANALOG_SEARCH = "analog_search"
    ATTRIBUTE_GENERATION = "attribute_generation"
    COINCIDENCE = "coincidence"
    IDENTITY = "identity"
    APPLICATION_GENERATION = "application_generation"
