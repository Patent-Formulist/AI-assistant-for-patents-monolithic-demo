import enum


class UIButton(str, enum.Enum):
    """Section of the patent page the user last opened."""

    ANALOGS_SEARCH = "ANALOGS_SEARCH"
    STATISTICS = "STATISTICS"
    IDENTITY = "IDENTITY"
