from datetime import datetime

from core.data_mapper.mapper import StaticMapper
from core.db.models.user import UserModel
from core.domain.user import User


class UserMapper(StaticMapper[User, UserModel, None]):
    @staticmethod
    async def to_model(user: User) -> UserModel:
        """Convert domain User to DB UserModel"""
        user_model = UserModel()

        if user.user_id:
            user_model.id = user.user_id
        if user.tg_id:
            user_model.tg_id = user.tg_id
        if user.email:
            user_model.email = user.email
        if user.username:
            user_model.username = user.username

        # Пароль
        if user.hashed_password:
            user_model.hashed_password = user.hashed_password

        # Персональная информация
        if user.first_name:
            user_model.first_name = user.first_name
        if user.last_name:
            user_model.last_name = user.last_name
        if user.avatar_url:
            user_model.avatar_url = user.avatar_url
        if hasattr(user, "bio") and user.bio is not None:
            user_model.bio = user.bio

        # Статус и верификация
        user_model.status = user.status or "PENDING"
        user_model.is_email_verified = user.is_email_verified or False
        if user.email_verified_at:
            user_model.email_verified_at = user.email_verified_at

        # Безопасность
        user_model.failed_login_attempts = user.failed_login_attempts or 0
        if user.locked_until:
            user_model.locked_until = user.locked_until
        if user.last_failed_login:
            user_model.last_failed_login = user.last_failed_login

        # Аудит
        if user.last_login_at:
            user_model.last_login_at = user.last_login_at
        if user.last_login_ip:
            user_model.last_login_ip = user.last_login_ip
        if user.last_activity_at:
            user_model.last_activity_at = user.last_activity_at

        # Временные метки
        if user.created_at:
            user_model.created_at = user.created_at
        if user.updated_at:
            user_model.updated_at = user.updated_at

        return user_model

    @staticmethod
    async def to_domain(user_model: UserModel) -> User:
        """Convert DB UserModel to domain User"""
        return User(
            user_id=user_model.id,
            tg_id=user_model.tg_id,
            email=user_model.email,
            username=user_model.username,
            hashed_password=user_model.hashed_password,
            first_name=user_model.first_name,
            last_name=user_model.last_name,
            avatar_url=user_model.avatar_url,
            bio=getattr(user_model, "bio", None),
            status=user_model.status or "PENDING",
            is_email_verified=user_model.is_email_verified or False,
            email_verified_at=user_model.email_verified_at,
            failed_login_attempts=user_model.failed_login_attempts or 0,
            locked_until=user_model.locked_until,
            last_failed_login=user_model.last_failed_login,
            last_login_at=user_model.last_login_at,
            last_login_ip=user_model.last_login_ip,
            last_activity_at=user_model.last_activity_at,
            created_at=user_model.created_at or datetime.now(),
            updated_at=user_model.updated_at or datetime.now(),
        )
