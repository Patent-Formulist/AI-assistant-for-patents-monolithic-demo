from abc import ABC, abstractmethod
from typing import Any


class BaseTableWriter(ABC):
    @abstractmethod
    def write(self, headers: list, rows: list, title: str = "table") -> Any:
        """
        Записывает таблицу в нужном формате

        Returns:
            Байтовое представление таблицы
        """
        pass
