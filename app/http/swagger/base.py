class BaseAPIResponse:
    """Base class for API responses"""

    @staticmethod
    def error(status_code: int, description: str, detail: str):
        return {
            status_code: {
                "description": description,
                "content": {"application/json": {"example": {"detail": detail}}},
            }
        }
