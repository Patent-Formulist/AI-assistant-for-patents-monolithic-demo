from pydantic import BaseModel, Field


class DrawingElementRequest(BaseModel):
    """Request model for creating/updating drawing element"""

    number: int = Field(..., description="Номер элемента")
    description: str = Field(..., description="Описание элемента")


class DrawingElementUpdateRequest(BaseModel):
    """Request model for updating drawing element"""

    description: str = Field(..., description="Описание элемента")


class DrawingElementReorderRequest(BaseModel):
    """Request model for reordering elements"""

    element_ids: list[int] = Field(..., description="Список ID элементов в новом порядке")


class DrawingFigureRequest(BaseModel):
    """Request model for creating/updating drawing figure"""

    number: int = Field(..., description="Номер фигуры")
    title: str = Field(..., description="Название/описание фигуры")
    element_ids: list[int] = Field(
        default_factory=list, description="Список ID элементов на фигуре"
    )


class DrawingFigureUpdateRequest(BaseModel):
    """Request model for updating drawing figure"""

    title: str = Field(..., description="Название/описание фигуры")
    element_ids: list[int] = Field(
        default_factory=list, description="Список ID элементов на фигуре"
    )


class DrawingImportRequest(BaseModel):
    """Request model for importing drawing elements as a list"""

    elements: list[str] = Field(..., description="Список описаний элементов")


class DrawingExportRequest(BaseModel):
    """Request model for exporting drawings"""

    format: str = Field(..., description="Формат экспорта: docx или xlsx")
