from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from core import logger
from core.dependencies.dependencies import get_db

logger = logger.get_logger(__name__)
SessionDep = Annotated[AsyncSession, Depends(get_db)]


def get_user_service(db: SessionDep):
    from app.service.user.user import UserService

    return UserService(session=db)


def get_user_processor(db: SessionDep):
    from app.service.user.processor import ProcessorUserService

    return ProcessorUserService(us=get_user_service(db))


def get_email_verification(db: SessionDep):
    from app.service.mail.mailer import Mailer
    from app.service.user.email_verification import EmailVerificationService
    from core.settings import get_settings

    settings = get_settings()
    return EmailVerificationService(
        session=db, mailer=Mailer(settings.mail), settings=settings.auth
    )
