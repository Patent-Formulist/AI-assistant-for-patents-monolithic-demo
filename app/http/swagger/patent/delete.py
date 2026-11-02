from fastapi import status

from app.http.swagger.base import BaseAPIResponse


class PatentDeleteResponses(BaseAPIResponse):
    """Response documentation for patent deletion endpoints"""

    @staticmethod
    def get_responses() -> dict:
        """Get all possible responses for patent deletion"""
        responses = {}

        # Success response
        responses[status.HTTP_200_OK] = {
            "description": "Patent successfully deleted",
            "content": {"application/json": {"example": {"patent_uuid": "432"}}},
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
                description="Patent deletion process failed",
                detail="Failed to delete patent from the system",
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
                description="Patent not found",
                detail="Patent not found or access denied",
            )
        )

        responses.update(
            BaseAPIResponse.error(
                status_code=status.HTTP_403_FORBIDDEN,
                description="Access denied",
                detail="User does not have permission to delete this patent",
            )
        )

        return responses
