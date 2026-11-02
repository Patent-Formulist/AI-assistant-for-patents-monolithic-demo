from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from core.db.db import Base
from core.db.mixins import SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    pass


class DrawingFigureModel(Base, TimestampMixin, SoftDeleteMixin):
    """Model for drawing figures (фигуры чертежей)"""

    __tablename__ = "drawing_figure"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    patent_id = Column(
        BigInteger,
        ForeignKey("patent.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID патента",
    )
    number = Column(Integer, nullable=False, comment="Номер фигуры (Фиг. 1, Фиг. 2, ...)")
    title = Column(String(500), nullable=False, comment="Название/описание фигуры")

    # Relationships
    patent = relationship("PatentModel", back_populates="drawing_figures")
    figure_elements = relationship(
        "FigureElementModel",
        back_populates="figure",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"DrawingFigure(id={self.id}, number={self.number}, title={self.title[:30]}...)"
