from dataclasses import dataclass


@dataclass
class PatentAttributeIDPair:
    attribute_id: int
    patent_id: int
    id: int | None = None
