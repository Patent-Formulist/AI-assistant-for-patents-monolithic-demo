from abc import ABC, abstractmethod


class BaseComponentGenerator(ABC):
    @abstractmethod
    async def generate(self, **kwargs):
        """Возвращает (headers, rows) или (None, None)"""
        pass
