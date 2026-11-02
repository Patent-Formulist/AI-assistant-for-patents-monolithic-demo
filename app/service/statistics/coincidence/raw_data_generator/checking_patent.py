import json

from app.service.attribute_tool import AttributeToolService
from app.service.base_checking_generator import BaseCheckingGenerator
from core import logger
from core.domain.attribute import Attribute
from core.domain.patent import Patent
from core.dto.attribute_sign import AttributeSignDetailDto, PatentAttributesSignDto
from core.enum.ai_purpose import AIPurpose

logger = logger.get_logger(__name__)


class CheckingPatentGenerator(BaseCheckingGenerator[PatentAttributesSignDto]):
    batch_name = "патент"
    """Generator of attribute signs for the main patent using LLM."""





