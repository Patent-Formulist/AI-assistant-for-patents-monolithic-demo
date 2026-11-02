from pydantic import BaseModel, Field


class ConsentRequest(BaseModel):
    document: str = Field(max_length=50)
    version: str = Field(max_length=50, description="The version the user saw")
    # E.g. cookie categories {"analytics": false}; free-form, stored as is
    choices: dict[str, bool] | None = None
