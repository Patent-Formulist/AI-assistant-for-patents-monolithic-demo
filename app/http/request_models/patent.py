from pydantic import BaseModel, Field

from core.enum.ui_button import UIButton


class PatentFieldsRequest(BaseModel):
    name: str | None = Field(
        default="",
        description="Name/title of the patent",
        examples=["Advanced Solar Panel System"],
    )
    search_query: str | None = Field(
        default=None,
        description="Search query used to find similar patents",
        examples=["solar panel efficiency"],
    )
    appointment: str | None = Field(
        default=None,
        description="Purpose or application of the invention",
        examples=["Renewable energy generation"],
    )
    construction: str | None = Field(
        default=None,
        description="Structural description of the invention",
        examples=["Multi-layer photovoltaic cells with cooling system"],
    )
    operation_principle: str | None = Field(
        default=None,
        description="How the invention works",
        examples=["Converts sunlight to electricity using semiconductor materials"],
    )
    technical_area: str | None = Field(
        default=None,
        description="Technical field/category of the invention",
        examples=["Renewable Energy, Photovoltaics"],
    )
    technical_result: str | None = Field(
        default=None,
        description="Technical advantages or results achieved",
        examples=["25% higher efficiency compared to existing solutions"],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Advanced Solar Panel System",
                    "search_query": "high efficiency solar panels",
                    "appointment": "Renewable energy generation for residential use",
                    "construction": "Multi-layer structure with anti-reflective coating",
                    "operation_principle": "Photon absorption and electron excitation",
                    "technical_area": "Renewable Energy, Semiconductor Technology",
                    "technical_result": "Improved energy conversion efficiency",
                }
            ]
        }
    }


class PatentNameRequest(BaseModel):
    patent_name: str = Field(
        ...,
        min_length=1,
        description="Название патента",
        examples=["Солнечная панель с повышенной эффективностью"],
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{"patent_name": "Солнечная панель с повышенной эффективностью"}]
        }
    }


class PatentIdRequest(BaseModel):
    patent_id: int = Field(..., description="ID патента", examples=[434])

    model_config = {"json_schema_extra": {"examples": [{"patent_id": 434}]}}


class LastUIButtonRequest(BaseModel):
    last_ui_button: UIButton = Field(
        ...,
        description="Последняя открытая секция: ANALOGS_SEARCH | STATISTICS | IDENTITY",
        examples=["STATISTICS"],
    )
