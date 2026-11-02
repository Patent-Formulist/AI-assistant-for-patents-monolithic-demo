from datetime import datetime

from app.http.request_models.analog import AnalogFieldsRequest
from app.http.response_models.analog import AnalogFieldsResponse
from core import logger
from core.data_mapper.mapper import StaticMapper
from core.db.models.analog import AnalogModel
from core.domain.analog import Analog
from core.dto.analog_request_mapping_context import AnalogRequestMappingContext

logger = logger.get_logger(__name__)


class AnalogMapper(StaticMapper[Analog, AnalogModel, AnalogFieldsRequest | AnalogFieldsResponse]):
    @staticmethod
    async def to_model(analog: Analog) -> AnalogModel:
        """Convert domain Analog to DB AnalogModel"""
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

        return analog_model

    @staticmethod
    async def to_domain(analog_model: AnalogModel) -> Analog:
        """Convert DB AnalogModel to domain Analog"""
        logger.info(f" {analog_model.abstract[:15]} _-----_{analog_model.claims[:15]}")
        abstract = analog_model.abstract or ""
        claims = analog_model.claims or ""
        title = analog_model.title or ""
        number = analog_model.number or ""
        link = analog_model.link or ""
        description = analog_model.description or ""

        return Analog(
            id=analog_model.id,
            title=title,
            analog_num=number,
            analog_link=link,
            abstract=abstract,
            claims=claims,
            description=description,
            created_at=analog_model.created_at or datetime.now(),
            updated_at=analog_model.updated_at or datetime.now(),
        )

    @staticmethod
    def from_pydantic_to_domain(dto: AnalogRequestMappingContext) -> Analog:
        return Analog(
            id=dto.analog.id,
            analog_num=dto.analog.analog_num,
            title=dto.request.title,
            claims=dto.request.claims,
            abstract=dto.request.abstract,
            description=dto.request.description,
            analog_link=dto.analog.analog_link,
        )
