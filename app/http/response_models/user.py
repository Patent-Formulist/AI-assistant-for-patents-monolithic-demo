from pydantic import BaseModel, EmailStr


class TokenResponse(BaseModel):
    access: str
    refresh: str | None = None

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "access": "eyJhbGciOiJIUzI1NiIs...",
                    "refresh": "eyJhbGciOiJIUzI1NiIs...",
                }
            ]
        },
    }


class UserResponse(BaseModel):
    id: str
    email: EmailStr

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "email": "user@example.com",
                }
            ]
        },
    }


class AuthResponse(TokenResponse):
    user: UserResponse

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access": "eyJhbGciOiJIUzI1NiIs...",
                    "refresh": "eyJhbGciOiJIUzI1NiIs...",
                    "user": {
                        "id": "123e4567-e89b-12d3-a456-426614174000",
                        "email": "user@example.com",
                    },
                }
            ]
        }
    }


class LogoutResponse(BaseModel):
    refresh_token: str

    model_config = {
        "json_schema_extra": {"examples": [{"refresh_token": "eyJhbGciOiJIUzI1NiIs..."}]}
    }


class UpAccessTokenResponse(BaseModel):
    access: str
    refresh: str
