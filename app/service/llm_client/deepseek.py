from app.service.llm_client.llm_client import LLMClient
from core import logger
from core.settings import DeepSeekSettings

logger = logger.get_logger(__name__)


class DeepSeekClient(LLMClient):
    """Клиент для работы с DeepSeek API"""

    def __init__(self, config: DeepSeekSettings):
        super().__init__(config)
