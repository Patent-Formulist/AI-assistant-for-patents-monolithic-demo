from fastapi import status

from app.http.swagger.base import BaseAPIResponse


class AnalogEditResponses(BaseAPIResponse):
    """Response documentation for analog edit endpoints"""

    @staticmethod
    def get_responses() -> dict:
        """Get all possible responses for analog edits"""
        responses = {}

        # Success response
        responses[status.HTTP_200_OK] = {
            "description": "Analog successfully updated",
            "content": {
                "application/json": {
                    "example": {"analog_uuid": "123e4567-e89b-12d3-a456-426614174000"}
                }
            },
        }

        # Error responses
        responses.update(
            BaseAPIResponse.error(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Invalid request data",
                detail="Invalid request data: Analog name cannot be empty",
            )
        )

        responses.update(
            BaseAPIResponse.error(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                description="Analog edit process failed",
                detail="Failed to update analog in the system",
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
                detail="User does not have permission to edit this analog",
            )
        )

        responses.update(
            BaseAPIResponse.error(
                status_code=status.HTTP_400_BAD_REQUEST,
                description="Invalid input data",
                detail="No valid fields provided for update",
            )
        )

        return responses
