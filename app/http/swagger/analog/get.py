from fastapi import status

from app.http.swagger.base import BaseAPIResponse


class AnalogsGetResponses(BaseAPIResponse):
    """Response documentation for multiple analogs retrieval"""

    @staticmethod
    def get_responses() -> dict:
        """Get all possible responses for multiple analogs retrieval"""
        responses = {}

        # Success response with multiple analogs
        responses[status.HTTP_200_OK] = {
            "description": "Analogs successfully retrieved",
            "content": {
                "application/json": {
                    "example": {
                        "analogs": {
                            "123e4567-e89b-12d3-a456-426614174000": {
                                "name": "Solar Panel Analog",
                                "search_query": "renewable energy solar efficiency",
                                "appointment": "Energy generation",
                                "construction": "Multi-layer photovoltaic cells",
                                "operation_principle": "Photoelectric effect",
                                "technical_area": "Renewable Energy",
                                "technical_result": "25% efficiency increase",
                                "created_at": "2023-10-01T12:00:00Z",
                                "updated_at": "2023-10-05T14:30:00Z",
                            },
                            "123e4567-e89b-12d3-a456-426614174001": {
                                "name": "Wind Turbine Analog",
                                "search_query": "wind power turbine efficiency",
                                "appointment": "Wind energy conversion",
                                "construction": "Composite blade design",
                                "operation_principle": "Aerodynamic lift",
                                "technical_area": "Wind Energy",
                                "technical_result": "15% higher output",
                                "created_at": "2023-10-02T10:00:00Z",
                                "updated_at": "2023-10-02T10:00:00Z",
                            },
                            "123e4567-e89b-12d3-a456-426614174002": {
                                "name": "Battery Storage Analog",
                                "search_query": "",
                                "appointment": "",
                                "construction": "",
                                "operation_principle": "",
                                "technical_area": "",
                                "technical_result": "",
                                "created_at": "2023-10-03T09:00:00Z",
                                "updated_at": "2023-10-03T09:00:00Z",
                            },
                        }
                    }
                }
            },
        }

        # Empty response - no analogs found
        responses[status.HTTP_200_OK] = {
            "description": "No analogs found for user",
            "content": {"application/json": {"example": {"analogs": {}}}},
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
                status_code=status.HTTP_404_NOT_FOUND,
                description="Analogs not found or access denied",
                detail="Analogs not found or access denied",
            )
        )

        responses.update(
            BaseAPIResponse.error(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Invalid data format",
                detail="Invalid UUID format",
            )
        )

        responses.update(
            BaseAPIResponse.error(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                description="Internal server error",
                detail="Internal server error",
            )
        )

        responses.update(
            BaseAPIResponse.error(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                description="Temporary service unavailable",
                detail="Temporary service unavailable. Please try again later.",
            )
        )

        return responses


class AnalogGetResponses(BaseAPIResponse):
    """Response documentation for single analog retrieval"""

    @staticmethod
    def get_responses() -> dict:
        """Get all possible responses for single analog retrieval"""
        responses = {}

        # Success response for getting single analog
        responses[status.HTTP_200_OK] = {
            "description": "Analog successfully retrieved",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/AnalogFieldsResponse"},
                    "examples": {
                        "full_analog": {
                            "summary": "Analog with all fields filled",
                            "value": {
                                "name": "Solar Panel Analog",
                                "search_query": "renewable energy solar efficiency",
                                "appointment": "Energy generation from solar radiation",
                                "construction": "Multi-layer photovoltaic cells with nano-coating",
                                "operation_principle": "Photoelectric effect with enhanced light absorption",
                                "technical_area": "Renewable Energy, Photovoltaics",
                                "technical_result": "25% increase in energy conversion efficiency",
                                "created_at": "2023-10-01T12:00:00Z",
                                "updated_at": "2023-10-05T14:30:00Z",
                            },
                        },
                        "empty_analog": {
                            "summary": "Analog with empty fields",
                            "value": {
                                "name": "",
                                "search_query": "",
                                "appointment": "",
                                "construction": "",
                                "operation_principle": "",
                                "technical_area": "",
                                "technical_result": "",
                                "created_at": "2023-10-01T12:00:00Z",
                                "updated_at": "2023-10-01T12:00:00Z",
                            },
                        },
                    },
                }
            },
        }

        # Empty analog response
        responses[status.HTTP_200_OK] = {
            "description": "Analog found but fields are empty",
            "content": {
                "application/json": {
                    "example": {
                        "name": "",
                        "search_query": "",
                        "appointment": "",
                        "construction": "",
                        "operation_principle": "",
                        "technical_area": "",
                        "technical_result": "",
                        "created_at": "2023-10-01T12:00:00Z",
                        "updated_at": "2023-10-01T12:00:00Z",
                    }
                }
            },
        }

        # Error responses
        responses.update(
            BaseAPIResponse.error(
                status_code=status.HTTP_400_BAD_REQUEST,
                description="Invalid analog ID format",
                detail="Invalid analog ID format",
            )
        )

        responses.update(
            BaseAPIResponse.error(
                status_code=status.HTTP_404_NOT_FOUND,
                description="Analog not found or access denied",
                detail="Analog not found or access denied",
            )
        )

        responses.update(
            BaseAPIResponse.error(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                description="Invalid data format",
                detail="Invalid UUID format",
            )
        )

        responses.update(
            BaseAPIResponse.error(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                description="Internal server error",
                detail="Internal server error",
            )
        )

        responses.update(
            BaseAPIResponse.error(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                description="Temporary service unavailable",
                detail="Temporary service unavailable. Please try again later.",
            )
        )

        return responses
