from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.http.request_models import LoginRequest
from app.http.request_models.user import (
    EmailVerificationRequest,
    LogoutRequest,
    RegistrationRequest,
    UpdateProfileRequest,
)
from app.http.response_models import AuthResponse, UpAccessTokenResponse, UserResponse
from app.http.swagger.user.auth_responses import AuthResponses
from app.service.legal.legal import LegalService
from app.service.token.processor import ProcessorTokenService
from app.service.token.token import TokenService
from app.service.user.email_verification import EmailVerificationService
from app.service.user.processor import ProcessorUserService
from app.service.user.user import UserService
from core import logger
from core.decorators.api_router import handle_exceptions
from core.dependencies.auth import CurrentUserId
from core.dependencies.client import ClientInfo, get_client_info
from core.dependencies.legal import get_legal_service
from core.dependencies.token import (
    get_token_processor,
    get_token_service,
)
from core.dependencies.user import (
    get_email_verification,
    get_user_processor,
    get_user_service,
)
from core.domain.token import Token
from core.domain.user import User
from core.dto.user import UserAuth, UserUpdate
from core.enum.token_type import TokenType
from core.exceptions import InvalidSchemeError, MissingHeaderError

router = APIRouter(prefix="/api/v2/users", tags=["User"])
logger = logger.get_logger(__name__)
SecurityDep = Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer(auto_error=False))]
ProcessorUserServiceDep = Annotated[ProcessorUserService, Depends(get_user_processor)]
ProcessorTokenServiceDep = Annotated[ProcessorTokenService, Depends(get_token_processor)]
TokenServiceDep = Annotated[TokenService, Depends(get_token_service)]
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
EmailVerificationDep = Annotated[EmailVerificationService, Depends(get_email_verification)]
LegalServiceDep = Annotated[LegalService, Depends(get_legal_service)]


#################################################################################
# POST
#################################################################################
@router.post("/logout", summary="Logout user", responses=AuthResponses.logout_responses())
@handle_exceptions
async def logout(
    request: LogoutRequest,
    processor: ProcessorUserServiceDep,
    token_service: TokenServiceDep,
):
    refresh_token = request.refresh_token
    await processor.logout(refresh_token, token_service)
    return JSONResponse(status_code=200, content={"message": "Logout is successful"})


@router.post(
    "/login",
    summary="User login",
    responses=AuthResponses.login_responses(),
    response_model=AuthResponse,
)
@handle_exceptions
async def login(
    login_request: LoginRequest,
    processor_user: ProcessorUserServiceDep,
    processor_token: ProcessorTokenServiceDep,
    user_service: UserServiceDep,
):
    dto = UserAuth(email=str(login_request.email), password=login_request.password)

    user: User = await processor_user.login(dto)

    if user.email is None:
        logger.error(f"User {user.user_id} has no email after login")
        raise HTTPException(status_code=500, detail="User account is misconfigured: missing email")

    token_pair = await processor_token.process_create_token_pair(
        user_id=user.user_id, user_service=user_service
    )

    return AuthResponse(
        user=UserResponse(id=str(user.user_id), email=user.email),
        access=token_pair.access_token,
        refresh=token_pair.refresh_token,
    )


@router.post(
    "/registration",
    summary="User registration",
    responses=AuthResponses.registration_responses(),
    response_model=AuthResponse,
)
@handle_exceptions
async def registration(
    registration_request: RegistrationRequest,
    processor_user: ProcessorUserServiceDep,
    processor_token: ProcessorTokenServiceDep,
    user_service: UserServiceDep,
    verification: EmailVerificationDep,
    legal: LegalServiceDep,
    client: Annotated[ClientInfo, Depends(get_client_info)],
):
    dto = UserAuth(email=registration_request.email.lower(), password=registration_request.password)
    accepted = [(d.document, d.version) for d in registration_request.accepted_documents]
    # Before creating the user: an outdated form must not leave a half-registered account
    legal.check_current(accepted)

    user: User = await processor_user.registration(dto)
    await legal.accept_many(user.user_id, accepted, client.ip_address, client.user_agent)
    await verification.send_quietly(user.user_id)

    if user.email is None:
        logger.error(f"User {user.user_id} has no email after login")
        raise HTTPException(status_code=500, detail="User account is misconfigured: missing email")

    token_pair = await processor_token.process_create_token_pair(
        user_id=user.user_id, user_service=user_service
    )
    assert user.email is not None, "Email must exist for authenticated user"

    return AuthResponse(
        user=UserResponse(id=str(user.user_id), email=user.email),
        access=token_pair.access_token,
        refresh=token_pair.refresh_token,
    )


@router.post(
    "/refresh",
    summary="Refresh access token",
    responses=AuthResponses.refresh_responses(),
    response_model=UpAccessTokenResponse,
)
@handle_exceptions
async def refresh(
    credentials: SecurityDep,
    processor_token: ProcessorTokenServiceDep,
    token_service: TokenServiceDep,
    user_service: UserServiceDep,
):
    if not credentials:
        raise MissingHeaderError
    if not credentials.scheme.lower() == "bearer":
        raise InvalidSchemeError

    refresh_token = credentials.credentials
    token: Token = await processor_token.process_check_token(
        token=refresh_token, expected_type=TokenType.REFRESH, user_service=user_service
    )
    user_id: int = await token_service.get_user_id_by_token_jti(token.jti)
    # Rotate: the used refresh token cannot be exchanged again
    await token_service.revoke_token(token.jti, reason="rotated")
    token_pair = await processor_token.process_create_token_pair(
        user_id=user_id, user_service=user_service
    )
    return UpAccessTokenResponse(access=token_pair.access_token, refresh=token_pair.refresh_token)


#################################################################################
# GET
#################################################################################
@router.get("/validate", summary="Check that the access token is still valid")
@handle_exceptions
async def validate(user_id: CurrentUserId):
    """Проверка «я ещё залогинен» для фронтенда.

    До переноса авторизации на бэкенд этот роут был ещё и целью `auth_request`
    в nginx и отдавал заголовок `X-User-Id`, который nginx подставлял в запрос.
    Теперь токен проверяет зависимость `get_current_user_id`, и заголовок не нужен.
    """
    return {"user_id": user_id}


#################################################################################
# PATCH
#################################################################################
@router.patch("/profile", summary="Update user profile")
@handle_exceptions
async def update_profile(
    request: UpdateProfileRequest,
    user_id: CurrentUserId,
    processor_user: ProcessorUserServiceDep,
    verification: EmailVerificationDep,
):
    update_dto = UserUpdate(
        email=request.email,
        username=request.username,
        first_name=request.first_name,
        last_name=request.last_name,
        avatar_url=request.avatar_url,
        bio=request.bio,
    )

    updated_user = await processor_user.update_profile(user_id, update_dto)
    await verification.send_if_changed(user_id, request.email)

    return JSONResponse(
        status_code=200,
        content={
            "message": "Profile updated successfully",
            "user": {
                "id": str(updated_user.user_id),
                "email": updated_user.email,
                "username": updated_user.username,
                "first_name": updated_user.first_name,
                "last_name": updated_user.last_name,
                "avatar_url": updated_user.avatar_url,
                "bio": getattr(updated_user, "bio", None),
            },
        },
    )


#################################################################################
# Email confirmation
#################################################################################
@router.get("/me", summary="Profile of the user, with the email confirmation state")
@handle_exceptions
async def me(user_id: CurrentUserId, user_service: UserServiceDep):
    user: User = await user_service.get_user_by_id(user_id)
    return {
        "id": str(user.user_id),
        "email": user.email,
        "is_email_verified": bool(user.is_email_verified),
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
    }


@router.post(
    "/email/verification",
    summary="Mail a new email confirmation link (at most once a minute)",
    status_code=202,
)
@handle_exceptions
async def send_verification(user_id: CurrentUserId, verification: EmailVerificationDep):
    return {"sent": await verification.send(user_id)}


@router.post("/email/verify", summary="Confirm the email with the token from the link")
@handle_exceptions
async def verify_email(request: EmailVerificationRequest, verification: EmailVerificationDep):
    await verification.verify(request.token)
    return {"verified": True}
