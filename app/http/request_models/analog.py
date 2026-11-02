from pydantic import BaseModel, Field


class AnalogFieldsRequest(BaseModel):
    id: str = Field(..., description="Unique identifier of the analog")
    analog_num: str = Field(..., description="Analog number")
    analog_link: str = Field(..., description="Analog link")
    title: str = Field(
        ...,
        description="Title of the analog patent",
        examples=["High-efficiency solar cell"],
        min_length=1,
    )
    abstract: str | None = Field(
        None,
        description="Abstract of the analog patent",
        examples=["A solar cell with enhanced light absorption..."],
    )
    claims: str | None = Field(
        None,
        description="Patent claims of the analog",
        examples=["1. A solar cell comprising..."],
    )
    description: str | None = Field(
        None,
        description="Detailed description of the analog",
        examples=["The invention relates to photovoltaic devices..."],
    )

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
                }
            ]
        }
    }


class AnalogRequest(BaseModel):
    """
    Запрос, содержащий словарь аналогов, где ключом является идентификатор аналога (строка),
    а значением — полные данные аналога (AnalogFieldsResponse).
    """

    patent_id: int = Field(..., description="ID патента")
    analogs: dict[str, AnalogFieldsRequest] = Field(
        ...,
        description="Словарь аналогов: ключ — идентификатор аналога (uuid или другой строковый id),"
        " значение — объект AnalogFieldsResponse",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "patent_id": "32",
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
                }
            ]
        }
    }
