from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class UpAccessTokenRequest(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class AcceptedDocument(BaseModel):
    document: str = Field(max_length=50)
    version: str = Field(max_length=50, description="The edition the user saw")


class RegistrationRequest(BaseModel):
    email: EmailStr = Field(
        ..., min_length=1, description="The login must contain at least 1 character."
    )
    password: str = Field(
        ..., min_length=1, description="The password must contain at least 1 character."
    )
    # Documents accepted with the registration form (GET /legal/documents)
    accepted_documents: list[AcceptedDocument] = Field(default_factory=list)


class EmailVerificationRequest(BaseModel):
    token: str = Field(min_length=1, description="The token from the confirmation link")


class LogoutRequest(BaseModel):
    refresh_token: str


class LoginRequest(BaseModel):
    email: EmailStr = Field(
        ..., min_length=1, description="The login must contain at least 1 character."
    )
    password: str = Field(
        ..., min_length=1, description="The password must contain at least 1 character."
    )


class UpdateProfileRequest(BaseModel):
    """DTO for updating user profile fields.
    All fields are optional — only provided non-null fields are applied.
    Empty strings are treated as null (field not changed).
    """

    email: EmailStr | None = None
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    avatar_url: str | None = None
    bio: str | None = None

    @model_validator(mode="before")
    @classmethod
    def empty_strings_to_none(cls, values: dict) -> dict:
        """Treat empty/whitespace-only strings as None so they are ignored on save."""
        return {
            k: (None if isinstance(v, str) and v.strip() == "" else v) for k, v in values.items()
        }

    @field_validator("username")
    @classmethod
    def username_valid(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if len(v) < 3:
            raise ValueError("username must be at least 3 characters")
        if len(v) > 32:
            raise ValueError("username must be at most 32 characters")
        if not v.replace("_", "").replace(".", "").isalnum():
            raise ValueError("username may only contain letters, digits, underscores and dots")
        return v

    @field_validator("first_name", "last_name")
    @classmethod
    def name_valid(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if len(v) > 64:
            raise ValueError("name field must be at most 64 characters")
        return v

    @field_validator("bio")
    @classmethod
    def bio_valid(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if len(v) > 300:
            raise ValueError("bio must be at most 300 characters")
        return v

    @field_validator("avatar_url")
    @classmethod
    def avatar_url_valid(cls, v: str | None) -> str | None:
        if v is None:
            return v
        v = v.strip()
        if not v.startswith(("http://", "https://")):
            raise ValueError("avatar_url must be a valid HTTP/HTTPS URL")
        return v
