from .service import ServiceError


class ServiceRepositoryError(ServiceError):
    """Repository service level error"""

    pass


class DatabaseError(ServiceRepositoryError):
    """Ошибка базы данных"""

    pass


class TransactionError(DatabaseError):
    """Ошибка транзакции"""

    pass


class BulkOperationError(DatabaseError):
    """Ошибка массовых операций"""

    pass


class ServiceRepositoryError(ServiceError):
    """Repository service level error"""

    pass


class RepositoryInputError(ServiceRepositoryError):
    """Error in the input data in the repository service"""

    pass
