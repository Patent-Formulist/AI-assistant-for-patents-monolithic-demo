from fastapi import status

from app.http.swagger.base import BaseAPIResponse


class AnalogDeleteResponses(BaseAPIResponse):
    """Response documentation for analog deletion endpoints"""

    @staticmethod
    def get_responses() -> dict:
        """Get all possible responses for analog deletion"""
        responses = {}

        # Success response
        responses[status.HTTP_200_OK] = {
            "description": "Analog successfully deleted",
            "content": {"application/json": {"example": {"analog_uuid": "432"}}},
        }

        # Error responses
        responses.update(
            BaseAPIResponse.error(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Invalid request data",
                detail="Invalid request data: Invalid UUID format",
            )
        )

        responses.update(
            BaseAPIResponse.error(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                description="Analog deletion process failed",
                detail="Failed to delete analog from the system",
            )
        )

        responses.update(
            BaseAPIResponse.error(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                description="Storage service temporarily unavailable",
                detail="Storage service temporarily unavailable",
            )
        )

        responses.update(
            BaseAPIResponse.error(
                status_code=status.HTTP_404_NOT_FOUND,
                description="Analog not found",
                detail="Analog not found or access denied",
            )
        )

        responses.update(
            BaseAPIResponse.error(
                status_code=status.HTTP_403_FORBIDDEN,
                description="Access denied",
                detail="User does not have permission to delete this analog",
            )
        )

        return responses
