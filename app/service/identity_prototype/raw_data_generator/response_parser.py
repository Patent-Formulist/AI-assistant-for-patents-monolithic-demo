from core import logger

logger = logger.get_logger(__name__)


class IdentityResponseParser:
    @staticmethod
    def split_lines(raw_response: str) -> list[str]:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")

    @staticmethod
    def parse_line(line: str, line_idx: int) -> tuple[str | None, str | None, str | None]:
        raise NotImplementedError("Демонстрационная заглушка: алгоритм не публикуется")
