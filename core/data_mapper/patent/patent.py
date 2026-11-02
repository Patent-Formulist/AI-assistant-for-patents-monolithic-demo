from datetime import datetime

from app.http.request_models.patent import PatentFieldsRequest
from app.http.response_models.patent import PatentFieldsResponse
from core.data_mapper.mapper import StaticMapper
from core.db.models.patent import PatentModel
from core.domain.patent import Patent


class PatentMapper(StaticMapper[Patent, PatentModel, None]):
    @staticmethod
    async def to_model(patent: Patent) -> PatentModel:
        patent_model = PatentModel()
        patent_model.id = patent.id
        patent_model.name = patent.name
        patent_model.search_query = patent.search_query
        patent_model.appointment = patent.appointment
        patent_model.construction = patent.construction
        patent_model.operation_principle = patent.operation_principle
        patent_model.technical_area = patent.technical_area
        patent_model.technical_result = patent.technical_result
        patent_model.created_at = patent.created_at if patent.created_at is not None else None
        patent_model.updated_at = patent.updated_at if patent.updated_at is not None else None

        return patent_model

    @staticmethod
    async def to_domain(model: PatentModel) -> Patent:
        return Patent(
            id=model.id,
            name=model.name,
            search_query=model.search_query,
            appointment=model.appointment,
            construction=model.construction,
            operation_principle=model.operation_principle,
            technical_area=model.technical_area,
            technical_result=model.technical_result,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def from_pydantic_to_domain(pydantic_model: PatentFieldsRequest, patent_id: int) -> Patent:
        return Patent(
            id=patent_id,
            name=pydantic_model.name,
            search_query=pydantic_model.search_query,
            appointment=pydantic_model.appointment,
            construction=pydantic_model.construction,
            operation_principle=pydantic_model.operation_principle,
            technical_area=pydantic_model.technical_area,
            technical_result=pydantic_model.technical_result,
            updated_at=datetime.utcnow(),
        )

    @staticmethod
    def to_pydantic(patent: Patent) -> PatentFieldsResponse:
        return PatentFieldsResponse(
            id=str(patent.id),
            name=patent.name,
            search_query=patent.search_query,
            appointment=patent.appointment,
            construction=patent.construction,
            operation_principle=patent.operation_principle,
            technical_area=patent.technical_area,
            technical_result=patent.technical_result,
        )
