from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Column, ForeignKey
from sqlalchemy.orm import relationship

from core.db.db import Base
from core.db.mixins import SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    pass


class FigureElementModel(Base, TimestampMixin, SoftDeleteMixin):
    """Model for many-to-many relationship between figures and elements"""

    __tablename__ = "figure_element"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    figure_id = Column(
        BigInteger,
        ForeignKey("drawing_figure.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID фигуры",
    )
    element_id = Column(
        BigInteger,
        ForeignKey("drawing_element.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID элемента",
    )

    # Relationships
    figure = relationship("DrawingFigureModel", back_populates="figure_elements")
    element = relationship("DrawingElementModel", back_populates="figure_elements")

    def __repr__(self) -> str:
        return f"FigureElement(figure_id={self.figure_id}, element_id={self.element_id})"
