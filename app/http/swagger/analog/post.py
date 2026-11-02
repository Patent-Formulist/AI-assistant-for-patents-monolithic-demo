from fastapi import status

from app.http.swagger.base import BaseAPIResponse


class AnalogCreationResponses(BaseAPIResponse):
    """Response documentation for analog creation endpoints"""

    @staticmethod
    def get_responses() -> dict:
        """Get all possible responses for analog creation"""
        responses = {}

        # Success response
        responses[status.HTTP_201_CREATED] = {
            "description": "Analog successfully created",
            "content": {
                "application/json": {
                    "example": {"analog_uuid": "123e4567-e89b-12d3-a456-426614174000"}
                }
            },
        }

        # Error responses
        responses.update(
            BaseAPIResponse.error(
                status_code=status.HTTP_400_BAD_REQUEST,
                description="Invalid user ID format",
                detail="Invalid user ID format",
            )
        )

        responses.update(
            BaseAPIResponse.error(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Invalid request data",
                detail="Invalid request data: Analog name is required",
            )
        )

        responses.update(
            BaseAPIResponse.error(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                description="Analog creation process failed",
                detail="Failed to create analog in the system",
            )
        )

        responses.update(
            BaseAPIResponse.error(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                description="Storage service temporarily unavailable",
                detail="Storage service temporarily unavailable",
            )
        )

        return responses
