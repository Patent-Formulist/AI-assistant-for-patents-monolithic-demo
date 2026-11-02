from collections.abc import Callable
from functools import wraps

from fastapi import HTTPException, status

from core import logger
from core.exceptions import (
    AccessDeniedError,
    AnalogCreationError,
    AnalogCreationLinkError,
    AnalogDeleteError,
    AnalogEditError,
    AnalogGetError,
    AnalogNotFoundError,
    ConsentRequiredError,
    ConsentVersionError,
    EmailNotVerifiedError,
    EmailVerificationError,
    IdentifyPrototypeGetError,
    InsufficientFundsError,
    InternalServerErrorException,
    LegalDocumentNotFoundError,
    LoginError,
    LogoutError,
    OrganizationConflictError,
    OrganizationNotFoundError,
    PatentCreationError,
    PatentDeleteError,
    PatentEditError,
    PatentGetError,
    PatentNotFoundError,
    PaymentNotFoundError,
    PaymentProviderError,
    PaymentsDisabledError,
    PipelinePreconditionError,
    RegistrationError,
    ResourceNotFoundError,
    ServiceRepositoryError,
    TooManyRequestsError,
)

logger = logger.get_logger(__name__)
AUTH_DOCSTRING = """
    ## Authentication
    - Requires JWT token in Authorization header (Bearer token)
    - The backend validates the token itself and derives the user ID from it
"""


def handle_exceptions(func: Callable) -> Callable:
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        # ---- Auth / token errors ----
        # MissingHeaderError, InvalidSchemeError, AccessTokenError, RefreshTokenError,
        # ValidationTokenError и JWTError обрабатываются на уровне приложения
        # (app/http/exception_handlers.py): они возникают и в зависимостях,
        # куда этот декоратор не достаёт.
        except RegistrationError as e:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Registration failed: {str(e)}",
            ) from e
        except PipelinePreconditionError as e:
            # The frontend shows its own text for 400 on pipeline starts
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
        except InsufficientFundsError as e:
            raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED, detail=str(e)) from e
        except AccessDeniedError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e
        except EmailVerificationError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
        except EmailNotVerifiedError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e
        except TooManyRequestsError as e:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e)) from e
        except ResourceNotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
        except OrganizationNotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
        except OrganizationConflictError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
        except LegalDocumentNotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
        except ConsentRequiredError as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e)) from e
        except ConsentVersionError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e)) from e
        except PaymentNotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
        except PaymentsDisabledError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)
            ) from e
        except PaymentProviderError as e:
            logger.error(f"Payment provider error: {e}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY, detail="Платёжный сервис не ответил"
            ) from e
        except LoginError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Login failed: {str(e)}",
            ) from e
        except LogoutError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Logout failed: {str(e)}",
            ) from e
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid request data: {str(e)}",
            ) from e
        except PatentCreationError as e:
            logger.error(f"Patent creation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Patent creation process failed",
            ) from e
        # NotFound is a PatentGetError subclass, so it must be caught first.
        except PatentNotFoundError as e:
            logger.error(f"Patent not found: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patents not found or access denied",
            ) from e
        except PatentGetError as e:
            logger.error(f"Patent get error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get patent",
            ) from e
        except PatentEditError as e:
            logger.error(f"Patent edit error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to edit patent",
            ) from e
        except PatentDeleteError as e:
            logger.error(f"Patent delete error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete patent",
            ) from e
        except IdentifyPrototypeGetError as e:
            logger.error(f"Identity prototype error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Identity prototypes not found for this patent",
            ) from e
        except AnalogCreationError as e:
            logger.error(f"Analog creation error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Analog creation process failed",
            ) from e
        # NotFound is an AnalogGetError subclass, so it must be caught first.
        except AnalogNotFoundError as e:
            logger.error(f"Analog not found: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Analog not found",
            ) from e
        except AnalogGetError as e:
            logger.error(f"Analog get error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get analog",
            ) from e
        except AnalogEditError as e:
            logger.error(f"Analog edit error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to edit analog",
            ) from e
        except AnalogDeleteError as e:
            logger.error(f"Analog delete error: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete analog",
            ) from e
        except AnalogCreationLinkError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Analog operation failed: {str(e)}",
            ) from e
        except ServiceRepositoryError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Storage service temporarily unavailable: {str(e)}",
            ) from e
        except InternalServerErrorException as e:
            logger.error(f"Internal server error in {func.__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            ) from e
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error",
            ) from e

    return wrapper


def auth_doc(endpoint):
    """Декоратор для добавления описания аутентификации к endpoint'ам"""
    if hasattr(endpoint, "__doc__") and endpoint.__doc__:
        endpoint.__doc__ = endpoint.__doc__.rstrip() + "\n\n" + AUTH_DOCSTRING
    else:
        endpoint.__doc__ = AUTH_DOCSTRING
    return endpoint
