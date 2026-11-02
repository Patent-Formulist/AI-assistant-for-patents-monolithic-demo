from dataclasses import dataclass


@dataclass
class UserAnalogIDPair:
    analog_id: int
    user_id: int
