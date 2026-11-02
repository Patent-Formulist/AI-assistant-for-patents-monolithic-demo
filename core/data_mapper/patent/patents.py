from app.http.response_models import PatentFieldsResponse, PatentResponse
from core.data_mapper.mapper import StaticMapper
from core.db.models.patent import PatentModel
from core.domain.patent import Patent


class PatentsMapper(StaticMapper[list[Patent], list[PatentModel], PatentResponse]):
    @staticmethod
    def to_model(patents: list[Patent]) -> list[PatentModel]:
        """Convert system patents to database models"""
        patent_models = []
        for patent in patents:
            patent_model = PatentModel()
            patent_model.id = patent.id
            patent_model.name = patent.name
            patent_model.search_query = patent.search_query or ""
            patent_model.appointment = patent.appointment or ""
            patent_model.construction = patent.construction or ""
            patent_model.operation_principle = patent.operation_principle or ""
            patent_model.technical_area = patent.technical_area or ""
            patent_model.technical_result = patent.technical_result or ""
            patent_model.created_at = patent.created_at if patent.created_at is not None else None
            patent_model.updated_at = patent.updated_at if patent.updated_at is not None else None

            patent_models.append(patent_model)
        return patent_models

    @staticmethod
    def to_domain(models: list[PatentModel]) -> list[Patent]:
        """Convert database models to system patents"""
        return [
            Patent(
                id=model.id,
                name=model.name,
                search_query=model.search_query or "",
                appointment=model.appointment or "",
                construction=model.construction or "",
                operation_principle=model.operation_principle or "",
                technical_area=model.technical_area or "",
                technical_result=model.technical_result or "",
                created_at=model.created_at or "",
                updated_at=model.updated_at or "",
            )
            for model in models
        ]

    @staticmethod
    def to_pydantic(patents: list[Patent]) -> PatentResponse:
        """Convert system patents to Pydantic responses"""
        return PatentResponse(
            patents={
                str(patent.id): PatentFieldsResponse(
                    id=str(patent.id),
                    name=patent.name,
                    search_query=patent.search_query,
                    appointment=patent.appointment,
                    construction=patent.construction,
                    operation_principle=patent.operation_principle,
                    technical_area=patent.technical_area,
                    technical_result=patent.technical_result,
                    created_at=patent.created_at,
                    updated_at=patent.updated_at,
                )
                for patent in patents
            }
        )
