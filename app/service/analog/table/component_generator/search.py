from app.service.table.component_generator import BaseComponentGenerator
from core import logger
from core.domain.analog import Analog
from core.dto.analog_attribute import AnalogAttributesGroupDto

logger = logger.get_logger(__name__)


class AnalogSearchComponentGenerator(BaseComponentGenerator):
    """Генератор для поисковой таблицы аналогов со всеми данными"""

    async def generate(self, analog: list[Analog], attribute: list[AnalogAttributesGroupDto]):
        logger.info("Start generate_analogs_search")
        try:
            headers = [
                "Number",
                "Title",
                "Url",
                "Abstract",
                "Claims",
                "Description",
                "Attributes",
            ]
            rows = []
            # Создаём словарь аналогов по id
            analog_by_id = {a.id: a for a in analog}

            for group in attribute:
                analog_obj = analog_by_id.get(group.analog_info.id)
                if not analog_obj:
                    continue

                # Формируем текст атрибутов с нумерацией
                attr_lines = []
                for idx, attr in enumerate(group.attributes, start=1):
                    attr_lines.append(f"{idx}. {attr.name}")
                attributes_text = "\n".join(attr_lines)

                row = [
                    analog_obj.analog_num,
                    analog_obj.title,
                    analog_obj.analog_link,
                    analog_obj.abstract,
                    analog_obj.claims,
                    analog_obj.description,
                    attributes_text,
                ]
                rows.append(row)

            return headers, rows
        except Exception as e:
            logger.error(e)
            raise
