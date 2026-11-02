from dataclasses import dataclass


@dataclass
class UserPatentIDPair:
    patent_id: int
    user_id: int

    def __post_init__(self):
        if not self.patent_id:
            raise ValueError("UserPatentIDPair patent_id not valid")
        if not self.user_id:
            raise ValueError("UserPatentIDPair user_id not valid")
