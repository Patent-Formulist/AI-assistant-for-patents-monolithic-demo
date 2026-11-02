import uuid

from sqlalchemy import TypeDecorator
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import CHAR


class GUID(TypeDecorator):
    impl = CHAR(36)
    cache_ok = True

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(UUID(as_uuid=True))

    def process_bind_param(self, value, dialect):
        if value is None:
            return None

        if isinstance(value, uuid.UUID):
            return value
        if isinstance(value, str):
            try:
                return uuid.UUID(value)
            except ValueError as e:
                raise ValueError(f"Invalid UUID string: '{value}'") from e
        raise TypeError(f"Expected UUID or string, got {type(value).__name__}")

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        return uuid.UUID(str(value))
