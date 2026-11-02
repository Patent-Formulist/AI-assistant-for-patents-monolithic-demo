import json

from app.service.attribute_tool import AttributeToolService
from app.service.base_checking_generator import BaseCheckingGenerator
from core import logger
from core.domain.analog import Analog
from core.domain.attribute import Attribute
from core.dto.attribute_sign import AnalogSignsDto, AttributeSignDetailDto
from core.enum.ai_purpose import AIPurpose

logger = logger.get_logger(__name__)


class CheckingAnalogGenerator(BaseCheckingGenerator[AnalogSignsDto]):
    """Generator of attribute signs for patent analogs using LLM."""





