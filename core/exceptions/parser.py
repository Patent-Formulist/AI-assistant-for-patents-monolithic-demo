from .service import ServiceError


class ParsingError(ServiceError):
    """Ошибка при парсинге данных"""

    pass


class ParserError(ParsingError):
    """Ошибка парсера"""

    pass


class NetworkError(ParsingError):
    """Ошибка сети при парсинге"""

    pass
