from datetime import datetime

from app.http.request_models.analog import AnalogFieldsRequest, AnalogRequest
from app.http.response_models.analog import AnalogFieldsResponse, AnalogResponse
from core.data_mapper.mapper import StaticMapper
from core.db.models.analog import AnalogModel
from core.domain.analog import Analog


class AnalogsMapper(
    StaticMapper[
        list[Analog],
        list[AnalogModel],
        AnalogFieldsRequest | AnalogFieldsResponse,
    ]
):
    @staticmethod
    async def to_model(analogs: list[Analog]) -> list[AnalogModel]:
        """Convert domain Analogs to DB AnalogModels"""
        analog_models = []
        for analog in analogs:
            analog_model = AnalogModel()
            if analog.id is not None:
                analog_model.id = analog.id
            analog_model.title = analog.title or ""
            analog_model.number = analog.analog_num or ""
            analog_model.link = analog.analog_link or ""
            analog_model.abstract = analog.abstract or ""
            analog_model.claims = analog.claims or ""
            analog_model.description = analog.description or ""

            if analog.created_at:
                analog_model.created_at = analog.created_at
            if analog.updated_at:
                analog_model.updated_at = analog.updated_at

            analog_models.append(analog_model)
        return analog_models

    @staticmethod
    async def to_domain(analog_models: list[AnalogModel]) -> list[Analog]:
        """Convert DB AnalogModels to domain Analogs"""
        return [
            Analog(
                id=model.id,
                title=model.title or "",
                analog_num=model.number or "",
                analog_link=model.link or "",
                abstract=model.abstract or "",
                claims=model.claims or "",
                description=model.description or "",
                created_at=model.created_at or datetime.now(),
                updated_at=model.updated_at or datetime.now(),
            )
            for model in analog_models
        ]

    @staticmethod
    def from_pydantic_to_domain(request: AnalogRequest) -> dict[int, Analog]:
        """Convert Pydantic DTOs to domain Analogs"""
        return {
            int(analog_data.id): Analog(
                id=int(analog_data.id),
                analog_num=analog_data.analog_num,
                title=analog_data.title,
                claims=analog_data.claims,
                abstract=analog_data.abstract,
                description=analog_data.description,
                analog_link=analog_data.analog_link,
            )
            for analog_data in request.analogs.values()
        }

    @staticmethod
    def to_pydantic_response(analogs: list[Analog]) -> AnalogResponse:
        """Convert domain Analogs to Pydantic AnalogResponse"""
        return AnalogResponse(
            analogs={
                str(analog.id): AnalogFieldsResponse(
                    id=str(analog.id),
                    title=analog.title,
                    analog_num=analog.analog_num,
                    analog_link=analog.analog_link,
                    abstract=analog.abstract,
                    claims=analog.claims,
                    description=analog.description,
                    created_at=analog.created_at,
                    updated_at=analog.updated_at,
                )
                for analog in analogs
            },
            total=len(analogs) if analogs else 0,
            page=1,
            size=len(analogs) if analogs else 10,
        )
