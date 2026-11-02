from app.service.table.component_generator import BaseComponentGenerator
from core import logger
from core.domain.analog import Analog

logger = logger.get_logger(__name__)


class AnalogLinksComponentGenerator(BaseComponentGenerator):
    """Провайдер для таблицы со ссылками на аналоги"""

    async def generate(self, analogs: list[Analog]) -> tuple[list[str], list[list[str]]]:
        logger.info("Start generate_analogs_link")
        try:
            headers = ["Number", "URL", "Title"]
            rows = [
                [str(analog.id), str(analog.analog_link), str(analog.title)] for analog in analogs
            ]
            return headers, rows

        except Exception as e:
            logger.error(e)
            raise
