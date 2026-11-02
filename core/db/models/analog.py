from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Column, String, Text
from sqlalchemy.orm import relationship

from core.db.db import Base
from core.db.mixins import SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    pass


class AnalogModel(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "analog"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    title = Column(String(500), default="")
    number = Column(String(100), default="")
    link = Column(String(500), default="")
    abstract = Column(Text, default="")
    claims = Column(Text, default="")
    description = Column(Text, default="")

    patent_analogs = relationship(
        "PatentAnalogModel", back_populates="analog", cascade="all, delete-orphan"
    )
    analog_attributes = relationship(
        "AnalogAttributeModel", back_populates="analog", cascade="all, delete-orphan"
    )
    identify_attributes = relationship(
        "IdentifyAttributeModel",
        foreign_keys="IdentifyAttributeModel.analog_id",
        back_populates="analog",
    )
