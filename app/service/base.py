from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any, ClassVar

from advanced_alchemy.exceptions import AdvancedAlchemyError, NotFoundError
from advanced_alchemy.repository.typing import ModelT, SQLAlchemyAsyncRepositoryT
from advanced_alchemy.service import SchemaDumpConfig, SQLAlchemyAsyncRepositoryService
from sqlalchemy.exc import SQLAlchemyError


class BaseService(SQLAlchemyAsyncRepositoryService[ModelT, SQLAlchemyAsyncRepositoryT]):
    """Base for domain services.

    create/update accept domain dataclasses directly: fields missing on the
    model are dropped, None fields are skipped, so column defaults apply on
    create and existing values are kept on update.

    Never commits: the transaction belongs to the caller (the request session
    from get_db, or the surrounding unit of work in background jobs).
    """

    schema_dump_config: ClassVar[SchemaDumpConfig] = SchemaDumpConfig(exclude_none=True)

    async def get_active(self, item_id: Any) -> ModelT:
        """Fetch a row that is not soft deleted (requires SoftDeleteMixin)."""
        model = await self.get_one_or_none(
            **{self.repository.id_attribute: item_id, "is_active": True}
        )
        if model is None:
            raise NotFoundError(f"{self.repository.model_type.__name__} {item_id} not found")
        return model

    @staticmethod
    @contextmanager
    def raise_as(error: type[Exception], message: str) -> Iterator[None]:
        """Re-raise storage errors as a domain error with context.

        Domain errors raised inside the block pass through unchanged.
        SQLAlchemyError covers raw session.execute calls that the repository
        does not wrap into AdvancedAlchemyError.
        """
        try:
            yield
        except (AdvancedAlchemyError, SQLAlchemyError) as e:
            raise error(f"{message}: {e}") from e
