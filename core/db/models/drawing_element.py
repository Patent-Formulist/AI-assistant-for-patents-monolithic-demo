from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Column, ForeignKey, Integer, Text
from sqlalchemy.orm import relationship

from core.db.db import Base
from core.db.mixins import SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    pass


class DrawingElementModel(Base, TimestampMixin, SoftDeleteMixin):
    """Model for drawing elements (составные части изобретения)"""

    __tablename__ = "drawing_element"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    patent_id = Column(
        BigInteger,
        ForeignKey("patent.id", ondelete="CASCADE"),
        nullable=False,
        comment="ID патента",
    )
    number = Column(Integer, nullable=False, comment="Номер элемента")
    description = Column(Text, nullable=False, comment="Описание элемента")

    # Relationships
    patent = relationship("PatentModel", back_populates="drawing_elements")
    figure_elements = relationship(
        "FigureElementModel",
        back_populates="element",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"DrawingElement(id={self.id}, number={self.number}, description={self.description[:30]}...)"
