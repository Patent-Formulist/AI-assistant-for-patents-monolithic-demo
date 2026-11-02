from app.service.table.component_generator import BaseComponentGenerator
from core import logger
from core.domain.analog import Analog

logger = logger.get_logger(__name__)


class AnalogMetadataComponentGenerator(BaseComponentGenerator):
    """Генератор для таблицы с абстрактами и claims аналогов"""

    async def generate(self, analogs: list[Analog]) -> tuple[list[str], list[list[str]]]:
        logger.info("Start generate_analogs_abstract_claims")

        try:
            headers = ["Number", "Title", "Claims", "Abstract", "Description"]
            rows = [
                [
                    analog.id,
                    analog.title,
                    analog.claims,
                    analog.abstract,
                    analog.description,
                ]
                for analog in analogs
            ]
            return headers, rows

        except Exception as e:
            logger.error(e)
            raise
