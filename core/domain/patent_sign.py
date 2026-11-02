from dataclasses import dataclass


@dataclass
class PatentAttributeSign:
    attribute_id: int
    patent_id: int
    sign: bool | None = None
