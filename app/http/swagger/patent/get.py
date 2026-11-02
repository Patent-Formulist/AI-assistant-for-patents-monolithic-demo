from fastapi import status

from app.http.swagger.base import BaseAPIResponse


class PatentsGetResponses(BaseAPIResponse):
    """Response documentation for multiple patents retrieval"""

    @staticmethod
    def get_responses() -> dict:
        """Get all possible responses for multiple patents retrieval"""
        responses = {}

        # Success response with multiple patents
        responses[status.HTTP_200_OK] = {
            "description": "Patents successfully retrieved",
            "content": {
                "application/json": {
                    "example": {
                        "patents": {
                            "123e4567-e89b-12d3-a456-426614174000": {
                                "name": "Solar Panel Innovation",
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
                                "name": "Wind Turbine Design",
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
                                "name": "Battery Storage System",
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

        # Empty response - no patents found
        responses[status.HTTP_200_OK] = {
            "description": "No patents found for user",
            "content": {"application/json": {"example": {"patents": {}}}},
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
                description="Patents not found or access denied",
                detail="Patents not found or access denied",
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


class PatentGetResponses(BaseAPIResponse):
    """Response documentation for single patent retrieval"""

    @staticmethod
    def get_responses() -> dict:
        """Get all possible responses for single patent retrieval"""
        responses = {}

        # Success response for getting single patent
        responses[status.HTTP_200_OK] = {
            "description": "Patent successfully retrieved",
            "content": {
                "application/json": {
                    "schema": {"$ref": "#/components/schemas/PatentFieldsResponse"},
                    "examples": {
                        "full_patent": {
                            "summary": "Patent with all fields filled",
                            "value": {
                                "name": "Solar Panel Innovation",
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
                        "empty_patent": {
                            "summary": "Patent with empty fields",
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

        # Empty patent response
        responses[status.HTTP_200_OK] = {
            "description": "Patent found but fields are empty",
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
                description="Invalid patent ID format",
                detail="Invalid patent ID format",
            )
        )

        responses.update(
            BaseAPIResponse.error(
                status_code=status.HTTP_404_NOT_FOUND,
                description="Patent not found or access denied",
                detail="Patent not found or access denied",
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
