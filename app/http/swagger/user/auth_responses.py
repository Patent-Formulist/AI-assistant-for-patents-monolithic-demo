from fastapi import status

from app.http.swagger.base import BaseAPIResponse


class AuthResponses(BaseAPIResponse):
    """Response documentation for auth service endpoints"""

    @staticmethod
    def login_responses() -> dict:
        responses = {}
        responses[status.HTTP_200_OK] = {
            "description": "User successfully logged in",
            "content": {
                "application/json": {
                    "example": {
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGci...",
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGci...",
                        "user": {
                            "id": "123e4567-e89b-12d3-a456-426614174000",
                            "email": "user@example.com",
                        },
                    }
                }
            },
        }
        responses.update(
            BaseAPIResponse.error(
                status_code=status.HTTP_401_UNAUTHORIZED,
                description="Invalid login credentials",
                detail="Invalid email or password",
            )
        )

        responses.update(
            BaseAPIResponse.error(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Invalid login format",
                detail="Email or password format is incorrect",
            )
        )
        responses.update(
            BaseAPIResponse.error(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                description="Internal server error during login",
                detail="Login process failed",
            )
        )
        return responses

    @staticmethod
    def registration_responses() -> dict:
        responses = {}
        responses[status.HTTP_200_OK] = {
            "description": "User successfully registered",
            "content": {
                "application/json": {
                    "example": {
                        "user": {
                            "user_id": "123e4567-e89b-12d3-a456-426614174000",
                            "email": "newuser@example.com",
                        },
                        "access": "eyJ0eXAiOiJKV1QiLCJhbGci...",
                        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGci...",
                    }
                }
            },
        }
        responses.update(
            BaseAPIResponse.error(
                status_code=status.HTTP_401_UNAUTHORIZED,
                description="User already exists",
                detail="User with this email already registered",
            )
        )
        responses.update(
            BaseAPIResponse.error(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Invalid registration format",
                detail="Invalid email or password format",
            )
        )
        responses.update(
            BaseAPIResponse.error(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                description="Internal server error during registration",
                detail="Registration process failed",
            )
        )
        return responses

    @staticmethod
    def validate_responses() -> dict:
        responses = {}
        responses[status.HTTP_200_OK] = {
            "description": "Token is valid",
            "content": {
                "application/json": {"example": {"message": "Token validation is successful"}}
            },
        }
        responses.update(
            BaseAPIResponse.error(
                status_code=status.HTTP_400_BAD_REQUEST,
                description="Bad Request — malformed or invalid authorization header or token type",
                detail="Authorization header missing, invalid authentication scheme, "
                "malformed token, or access token used instead of refresh token",
            )
        )

        responses.update(
            BaseAPIResponse.error(
                status_code=status.HTTP_401_UNAUTHORIZED,
                description="Unauthorized — access token validation failed",
                detail="Access token expired, invalid, revoked, signature check failed "
                "or user associated with the token does not exist",
            )
        )
        return responses

    @staticmethod
    def refresh_responses() -> dict:
        responses = {}
        responses[status.HTTP_200_OK] = {
            "description": "Access token successfully refreshed",
            "content": {
                "application/json": {
                    "example": {
                        "access": "new_access_token_value",
                        "refresh": "new_refresh_token_value",
                    }
                }
            },
        }
        responses.update(
            BaseAPIResponse.error(
                status_code=status.HTTP_400_BAD_REQUEST,
                description="Bad Request — malformed or invalid authorization header or token type",
                detail="Authorization header missing, invalid authentication scheme, "
                "malformed token, or access token used instead of refresh token",
            )
        )

        responses.update(
            BaseAPIResponse.error(
                status_code=status.HTTP_401_UNAUTHORIZED,
                description="Unauthorized — refresh token validation failed",
                detail="Refresh token expired, invalid, revoked, signature check failed, "
                "or user associated with the token does not exist",
            )
        )
        return responses

    @staticmethod
    def logout_responses() -> dict:
        responses = {}
        responses[status.HTTP_200_OK] = {
            "description": "User successfully logged out",
            "content": {"application/json": {"example": {"message": "Logout is successful"}}},
        }
        responses.update(
            BaseAPIResponse.error(
                status_code=status.HTTP_400_BAD_REQUEST,
                description="Invalid token type",
                detail="Only refresh tokens can be used for logout",
            )
        )
        responses.update(
            BaseAPIResponse.error(
                status_code=status.HTTP_401_UNAUTHORIZED,
                description="Invalid or expired refresh token",
                detail="Token validation failed",
            )
        )
        return responses

    @staticmethod
    def health_check_responses() -> dict:
        return {
            status.HTTP_200_OK: {
                "description": "Auth service health check",
                "content": {
                    "application/json": {"example": {"status": "healthy", "service": "auth"}}
                },
            }
        }
