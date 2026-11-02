from datetime import datetime

from pydantic import BaseModel, Field


class AnalogFieldsResponse(BaseModel):
    id: str | None = Field(None, description="Unique identifier of the analog")
    title: str | None = Field(None, description="Title of the analog patent")
    analog_num: str | None = Field(None, description="Official number of the analog patent")
    analog_link: str | None = Field(None, description="URL link to the analog patent document")
    abstract: str | None = Field(None, description="Abstract of the analog patent")
    claims: str | None = Field(None, description="Patent claims of the analog")
    description: str | None = Field(None, description="Detailed description of the analog")
    created_at: datetime | None = Field(None, description="Creation timestamp")
    updated_at: datetime | None = Field(None, description="Last update timestamp")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "32",
                    "title": "High-efficiency solar cell",
                    "analog_num": "US20210012345A1",
                    "analog_link": "https://patents.google.com/patent/US20210012345A1",
                    "abstract": "A solar cell with multi-junction structure achieving 30% efficiency.",
                    "claims": "1. A photovoltaic cell comprising a first layer of InGaP...",
                    "description": "The present disclosure provides a solar cell with improved efficiency...",
                    "created_at": "2023-01-15T10:30:00",
                    "updated_at": "2023-01-15T10:30:00",
                }
            ]
        }
    }


class AnalogResponse(BaseModel):
    """
    Ответ, содержащий словарь аналогов, где ключом является идентификатор аналога (строка),
    а значением — полные данные аналога (AnalogFieldsResponse).
    """

    analogs: dict[str, AnalogFieldsResponse] = Field(
        ...,
        description="Словарь аналогов: ключ — идентификатор аналога (uuid или другой строковый id),"
        " значение — объект AnalogFieldsResponse",
    )
    # Опционально можно добавить метаданные пагинации, если это список
    total: int | None = Field(None, description="Общее количество аналогов (Не реализовано)")
    page: int | None = Field(None, description="Номер текущей страницы (Не реализовано)")
    size: int | None = Field(None, description="Количество элементов на странице (Не реализовано)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "analogs": {
                        "1": {
                            "id": "32",
                            "title": "High-efficiency solar cell",
                            "analog_num": "US20210012345A1",
                            "analog_link": "https://patents.google.com/patent/US20210012345A1",
                            "abstract": "A solar cell with multi-junction structure achieving 30% efficiency.",
                            "claims": "1. A photovoltaic cell comprising a first layer of InGaP...",
                            "description": "The present disclosure provides a solar cell with improved efficiency...",
                            "created_at": "2023-01-15T10:30:00",
                            "updated_at": "2023-01-15T10:30:00",
                        },
                        "2": {
                            "id": "34",
                            "title": "Advanced wind turbine design",
                            "analog_num": "EP38765432B1",
                            "analog_link": "https://worldwide.espacenet.com/patent/EP38765432B1",
                            "abstract": "A vertical-axis wind turbine with noise reduction features.",
                            "claims": "1. A wind turbine comprising a rotor with variable pitch blades...",
                            "description": "The invention relates to wind turbines for urban environments...",
                            "created_at": "2023-02-20T09:15:00",
                            "updated_at": "2023-02-20T09:15:00",
                        },
                    },
                    "total": 2,
                    "page": 1,
                    "size": 10,
                }
            ]
        }
    }


class AnalogUUIDResponse(BaseModel):
    analog_uuid: str = Field(
        ...,
        min_length=1,
        description="ID аналога (В будующем возможен переход на уникальный идентификатор в формате UUID7)",
        examples=["152"],
    )
    model_config = {"json_schema_extra": {"examples": [{"analog_uuid": "152"}]}}
