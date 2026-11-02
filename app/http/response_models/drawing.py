from pydantic import BaseModel, ConfigDict, Field


class DrawingElementResponse(BaseModel):
    """Response model for drawing element"""

    id: int = Field(..., description="ID элемента")
    patent_id: int = Field(..., description="ID патента")
    number: int = Field(..., description="Номер элемента")
    description: str = Field(..., description="Описание элемента")

    model_config = ConfigDict(from_attributes=True)


class DrawingElementListResponse(BaseModel):
    """Response model for list of drawing elements"""

    elements: list[DrawingElementResponse] = Field(
        default_factory=list, description="Список элементов"
    )


class DrawingFigureElementResponse(BaseModel):
    """Response model for element in figure table"""

    number: int = Field(..., description="Номер элемента")
    description: str = Field(..., description="Описание элемента")


class DrawingFigureResponse(BaseModel):
    """Response model for drawing figure"""

    id: int = Field(..., description="ID фигуры")
    patent_id: int = Field(..., description="ID патента")
    number: int = Field(..., description="Номер фигуры")
    title: str = Field(..., description="Название/описание фигуры")
    elements: list[DrawingFigureElementResponse] = Field(
        default_factory=list, description="Элементы на фигуре"
    )

    model_config = ConfigDict(from_attributes=True)


class DrawingFigureListResponse(BaseModel):
    """Response model for list of drawing figures"""

    figures: list[DrawingFigureResponse] = Field(default_factory=list, description="Список фигур")


class DrawingImportResponse(BaseModel):
    """Response model for import operation"""

    imported_count: int = Field(..., description="Количество импортированных элементов")
    elements: list[DrawingElementResponse] = Field(
        default_factory=list, description="Импортированные элементы"
    )


class DrawingExportResponse(BaseModel):
    """Response model for export operation"""

    file_url: str = Field(..., description="URL для скачивания файла")
    filename: str = Field(..., description="Имя файла")
