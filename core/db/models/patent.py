from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Column, String, Text
from sqlalchemy.orm import relationship

from core.db.db import Base
from core.db.mixins import SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    pass


class PatentModel(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "patent"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(500), nullable=False)
    search_query = Column(Text, nullable=False, default="")
    appointment = Column(Text, nullable=False, default="")
    construction = Column(Text, nullable=False, default="")
    operation_principle = Column(Text, nullable=False, default="")
    technical_area = Column(Text, nullable=False, default="")
    technical_result = Column(Text, nullable=False, default="")

    user_patents = relationship("UserPatentModel", back_populates="patent")
    patent_attributes = relationship("PatentAttributeModel", back_populates="patent")
    patent_analogs = relationship(
        "PatentAnalogModel",
        back_populates="patent",
        cascade="all, delete-orphan",
    )
    identify_attributes = relationship(
        "IdentifyAttributeModel",
        foreign_keys="IdentifyAttributeModel.patent_id",
        back_populates="patent",
    )
    drawing_elements = relationship(
        "DrawingElementModel",
        back_populates="patent",
        cascade="all, delete-orphan",
    )
    drawing_figures = relationship(
        "DrawingFigureModel",
        back_populates="patent",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"Patent(id={self.id}, name={self.name[:50]}...)"
