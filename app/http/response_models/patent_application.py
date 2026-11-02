from datetime import datetime

from pydantic import BaseModel, Field


class PatentApplicationResponse(BaseModel):
    id: int | None = None
    patent_id: int
    abstract: str | None = None
    claims: list[str] | None = None
    description: str | None = None
    generated_at: datetime | None = None
    is_outdated: bool = False

    model_config = {"from_attributes": True}


class ClaimNode(BaseModel):
    """A single claim with its dependency metadata."""

    number: int = Field(..., description="Номер пункта формулы")
    text: str = Field(..., description="Текст пункта (без ведущего номера)")
    is_independent: bool = Field(..., description="Независимый пункт (не ссылается на другие)")
    depends_on: list[int] = Field(
        default_factory=list, description="Номера пунктов, от которых зависит"
    )
    family: int = Field(..., description="Номер корневого независимого пункта семьи")
    color: str = Field(..., description="Цвет семьи (hex) для индикатора")


class ClaimsFamily(BaseModel):
    """A group of claims sharing one root independent claim."""

    root: int = Field(..., description="Номер корневого независимого пункта")
    color: str = Field(..., description="Цвет семьи (hex)")
    members: list[int] = Field(default_factory=list, description="Номера пунктов, входящих в семью")


class ClaimsGraphResponse(BaseModel):
    """Dependency graph of the claims (formula) for the family indicator."""

    claims: list[ClaimNode] = Field(default_factory=list)
    families: list[ClaimsFamily] = Field(default_factory=list)
