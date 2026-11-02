class BaseProcessorError(Exception):
    """Базовое исключение для всех ошибок процессоров"""

    pass


class AnalogsCreationLinkError(BaseProcessorError):
    """Ошибка при создании ссылоки на аналог"""

    pass


class PatentAnalogsCreationLinkError(BaseProcessorError):
    """Ошибка при создании ссылок на аналоги"""

    pass


class AnalogsCreationMetadataError(BaseProcessorError):
    """Ошибка при создании данных аналога"""

    pass


class PatentAnalogsCreationMetadataError(BaseProcessorError):
    """Ошибка при создании данных аналогов"""

    pass


class PatentAnalogCreationMetadataError(BaseProcessorError):
    """Ошибка при создании данных аналога"""

    pass


class PatentAnalogsCreationSearchError(BaseProcessorError):
    """Ошибка при создании информации о поиска аналогов"""

    pass


class PatentAnalogsEditSearchError(BaseProcessorError):
    """Ошибка при редактирования информации о поиска аналогов"""

    pass


class AnalogCreationSearchError(BaseProcessorError):
    """Ошибка при создании информации о аналоге"""

    pass


class AttributeGenerationError(BaseProcessorError):
    """Ошибка при генерации атрибутов"""

    pass


class IdentityGenerationError(BaseProcessorError):
    """Ошибка при выявление пратотипа"""

    pass


class PipelinePreconditionError(Exception):
    """A pipeline cannot run yet: the data it needs is missing (API answers 400).

    The message is shown to the user as is.
    """
