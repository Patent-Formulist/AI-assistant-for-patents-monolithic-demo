from dataclasses import dataclass


@dataclass
class UserBase:
    email: str


@dataclass
class UserAuth(UserBase):
    password: str
    user_id: str | None = None


@dataclass
class UserUpdate:
    email: str | None = None
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    avatar_url: str | None = None
    bio: str | None = None
