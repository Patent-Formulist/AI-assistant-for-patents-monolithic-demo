from dataclasses import dataclass

from app.http.request_models.analog import AnalogFieldsRequest
from core.domain.analog import Analog


@dataclass
class AnalogRequestMappingContext:
    analog: Analog
    request: AnalogFieldsRequest
