from pydantic import BaseModel, Field


class PatentFieldsResponse(BaseModel):
    id: str = Field(..., description="Unique identifier of the patent")
    name: str = Field(..., description="Name/title of the patent")
    search_query: str | None = Field(None, description="Search query used to find similar patents")
    appointment: str | None = Field(None, description="Purpose or application of the invention")
    construction: str | None = Field(None, description="Structural description of the invention")
    operation_principle: str | None = Field(None, description="How the invention works")
    technical_area: str | None = Field(
        None, description="Technical field/category of the invention"
    )
    technical_result: str | None = Field(
        None, description="Technical advantages or results achieved"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "42",
                    "name": "Advanced Solar Panel System",
                    "search_query": "solar panel efficiency",
                    "appointment": "Renewable energy generation",
                    "construction": "Multi-layer photovoltaic cells with cooling system",
                    "operation_principle": "Converts sunlight to electricity using semiconductor materials",
                    "technical_area": "Renewable Energy, Photovoltaics",
                    "technical_result": "25% higher efficiency compared to existing solutions",
                }
            ]
        }
    }


class PatentResponse(BaseModel):
    """
    Ответ, содержащий словарь патентов, где ключом является идентификатор патента (строка),
    а значением — полные данные патента (PatentFieldsResponse).
    """

    patents: dict[str, PatentFieldsResponse] = Field(
        ...,
        description="Словарь патентов: ключ — идентификатор патента (uuid или другой строковый id), значение — объект PatentFieldsResponse",
    )
    # Опционально можно добавить метаданные пагинации, если это список
    total: int | None = Field(None, description="Общее количество патентов (Не реализовано)")
    page: int | None = Field(None, description="Номер текущей страницы (Не реализовано)")
    size: int | None = Field(None, description="Количество элементов на странице (Не реализовано)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "patents": {
                        "550": {
                            "id": "42",
                            "name": "Солнечная панель с повышенной эффективностью",
                            "search_query": "высокоэффективная солнечная панель",
                            "appointment": "Генерация электроэнергии для жилых домов",
                            "construction": "Многослойная структура с антибликовым покрытием",
                            "operation_principle": "Фотовольтаический эффект в полупроводниках",
                            "technical_area": "Возобновляемая энергетика, полупроводники",
                            "technical_result": "Повышение КПД на 20%",
                            "created_at": "2023-02-10T12:00:00",
                            "updated_at": "2023-02-10T12:00:00",
                        },
                        "660": {
                            "id": "43",
                            "name": "Ветрогенератор для городской среды",
                            "search_query": "городской ветрогенератор",
                            "appointment": "Энергоснабжение высотных зданий",
                            "construction": "Вертикально-осевая конструкция с шумоподавлением",
                            "operation_principle": "Преобразование кинетической энергии ветра",
                            "technical_area": "Ветроэнергетика",
                            "technical_result": "Снижение шума на 30%",
                            "created_at": "2023-02-11T14:30:00",
                            "updated_at": "2023-02-11T14:30:00",
                        },
                    },
                    "total": 2,
                    "page": 1,
                    "size": 10,
                }
            ]
        }
    }


class PatentUUIDResponse(BaseModel):
    patent_uuid: str = Field(
        ...,
        min_length=1,
        description="ID патента (В будующем возможен переход на уникальный идентификатор в формате UUID7)",
        examples=["152"],
    )
    model_config = {"json_schema_extra": {"examples": [{"patent_uuid": "152"}]}}


class PatentProgressResponse(BaseModel):
    """
    Состояние пользовательского UI прогресса по пайплайну патента.
    Фронтенд использует это при reload, чтобы понять,
    какую секцию показать пользователю.
    """

    last_ui_button: str | None = Field(
        None,
        description="Последняя нажатая кнопка: ANALOGS_SEARCH | STATISTICS | IDENTITY",
        examples=["STATISTICS"],
    )
    analogs_search_pipeline_state: str | None = Field(
        None,
        description="Analogs search pipeline state (PENDING/RUNNING/COMPLETED/FAILED)",
        examples=["COMPLETED"],
    )
    statistics_pipeline_state: str | None = Field(None, description="Statistics FSM state")
    statistics_pipeline_stage: str | None = Field(
        None, description="Statistics FSM stage (stage_1..stage_6)"
    )
    identity_pipeline_state: str | None = Field(None, description="Identity pipeline state")
    pipeline_error: str | None = Field(None, description="Last pipeline error")
