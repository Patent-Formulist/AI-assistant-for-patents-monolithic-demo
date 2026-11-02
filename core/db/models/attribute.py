from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Column, Index, String
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from sqlalchemy.orm import relationship

from core.db.db import Base
from core.db.mixins import SoftDeleteMixin, TimestampMixin
from core.enum.attribute_type import AttributeType

if TYPE_CHECKING:
    pass


class AttributeModel(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "attributes"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(1000), nullable=False)
    attribute_type = Column(
        PGEnum(AttributeType, name="attribute_type"),
        nullable=False,
        comment="Тип атрибута",
    )

    patent_attributes = relationship(
        "PatentAttributeModel", back_populates="attribute", cascade="all, delete-orphan"
    )
    analog_attributes = relationship(
        "AnalogAttributeModel", back_populates="attribute", cascade="all, delete-orphan"
    )
    identify_attributes_as_analog = relationship(
        "IdentifyAttributeModel",
        foreign_keys="IdentifyAttributeModel.analog_attribute_id",
        back_populates="analog_attribute",
    )

    identify_attributes_as_patent = relationship(
        "IdentifyAttributeModel",
        foreign_keys="IdentifyAttributeModel.patent_attribute_id",
        back_populates="patent_attribute",
    )

    identify_attributes_as_general = relationship(
        "IdentifyAttributeModel",
        foreign_keys="IdentifyAttributeModel.general_attribute_id",
        back_populates="general_attribute",
    )

    __table_args__ = (
        Index("idx_attribute_name", "name"),
        Index("idx_attribute_type", "attribute_type"),
    )

    def __repr__(self):
        return f"<Attribute(id={self.id}, name='{self.name}')>"

    def __str__(self):
        return self.name
