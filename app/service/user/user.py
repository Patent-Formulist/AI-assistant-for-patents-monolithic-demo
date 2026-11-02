from app.service.base import BaseService
from app.service.user.repository import UserRepository
from core import logger
from core.data_mapper.user import UserMapper
from core.db.models.user import UserModel
from core.domain.user import User
from core.dto.user import UserUpdate
from core.enum.user_status import UserStatus

logger = logger.get_logger(__name__)


class UserService(BaseService[UserModel, UserRepository]):
    """User accounts.

    Missing users and invalid input raise ValueError: the auth processors and
    handle_exceptions rely on it (422 or wrapped into Login/RegistrationError).
    """

    repository_type = UserRepository

    async def create_user_by_tg_id(self, tg_id: str) -> int:
        """Create user by Telegram ID."""
        if not tg_id:
            raise ValueError("tg_id cannot be empty")
        if await self._find(UserModel.tg_id == tg_id):
            raise ValueError(f"User with tg_id {tg_id} already exists")

        user = await self._create_user(UserModel(tg_id=tg_id, status=UserStatus.ACTIVE.value))
        return user.user_id

    async def create_user_by_email(self, email: str, hashed_password: str) -> User:
        """Create user by email."""
        if not email or "@" not in email:
            raise ValueError("Invalid email format")
        if await self._find(UserModel.email == email):
            raise ValueError(f"User with email {email} already exists")

        return await self._create_user(
            UserModel(email=email, status=UserStatus.ACTIVE.value, hashed_password=hashed_password)
        )

    async def get_user_by_tg_id(self, tg_id: str) -> User:
        return await self._get_user(UserModel.tg_id == tg_id, str(tg_id))

    async def get_user_by_id(self, user_id: int) -> User:
        return await self._get_user(UserModel.id == user_id, str(user_id))

    async def get_user_by_email(self, email: str) -> User:
        return await self._get_user(UserModel.email == email, email)

    async def update_user_profile(self, user_id: int, update_data: UserUpdate) -> User:
        logger.debug(f"Start updating user profile {user_id}")
        user_model = await self._find(UserModel.id == user_id)
        if user_model is None:
            raise ValueError(f"User {user_id} not found")

        new_email = update_data.email.lower() if update_data.email is not None else None
        if new_email is not None and new_email != user_model.email:
            if await self._find(UserModel.email == new_email):
                raise ValueError(f"Email {new_email} is already taken")
            user_model.email = new_email
            # A new address is unconfirmed until its own link is followed
            user_model.is_email_verified = False
            user_model.email_verified_at = None

        for field in ("username", "first_name", "last_name", "avatar_url", "bio"):
            value = getattr(update_data, field, None)
            if value is not None:
                setattr(user_model, field, value)

        try:
            updated = await self.update(user_model)
        except Exception as e:
            logger.error(f"Failed to update user profile: {e}")
            raise ValueError(f"Error updating user profile: {e}") from e
        return await UserMapper.to_domain(updated)

    async def _create_user(self, user_model: UserModel) -> User:
        try:
            saved = await self.create(user_model)
        except Exception as e:
            logger.error(f"Failed to save user to database: {e}")
            raise ValueError(f"Database save failed: {e}") from e
        return await UserMapper.to_domain(saved)

    async def _get_user(self, condition, label: str) -> User:
        user_model = await self._find(condition)
        if user_model is None:
            logger.debug(f"User {label} not found")
            raise ValueError(f"User {label} not found")
        return await UserMapper.to_domain(user_model)

    async def _find(self, condition) -> UserModel | None:
        try:
            return await self.get_one_or_none(condition)
        except Exception as e:
            logger.error(f"Failed to get user: {e}")
            raise ValueError(f"Database query failed: {e}") from e
