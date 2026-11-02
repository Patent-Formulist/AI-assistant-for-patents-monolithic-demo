from pydantic import BaseModel, Field


class PatentApplicationUpdateRequest(BaseModel):
    abstract: str | None = Field(None, description="Реферат")
    claims: list[str] | None = Field(
        None, description="Формула изобретения (пронумерованные пункты)"
    )
    description: str | None = Field(None, description="Описание изобретения")


class PatentApplicationExportRequest(BaseModel):
    format: str = Field(default="docx", description="Формат экспорта: docx")
