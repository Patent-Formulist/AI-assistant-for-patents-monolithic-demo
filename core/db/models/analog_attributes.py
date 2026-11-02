from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Column, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship

from core.db.db import Base
from core.db.mixins import SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    pass


class AnalogAttributeModel(Base, TimestampMixin, SoftDeleteMixin):
    """Модель для связи аналогов с атрибутами"""

    __tablename__ = "analog_attributes"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    analog_id = Column(
        BigInteger,
        ForeignKey("analog.id", ondelete="CASCADE", name="fk_analog_attribute_analog_id"),
        nullable=False,
        comment="ID аналога",
    )
    attribute_id = Column(
        BigInteger,
        ForeignKey("attributes.id", ondelete="CASCADE", name="fk_analog_attribute_attribute_id"),
        nullable=False,
        comment="ID атрибута",
    )
    analog = relationship("AnalogModel", back_populates="analog_attributes", lazy="joined")
    attribute = relationship("AttributeModel", back_populates="analog_attributes", lazy="joined")
    __table_args__ = (
        # Уникальность пары аналог-атрибут
        UniqueConstraint("analog_id", "attribute_id", name="uq_analog_attribute"),
        # Индексы для ускорения поиска
        Index("idx_analog_attribute_analog_id", "analog_id"),
        Index("idx_analog_attribute_attribute_id", "attribute_id"),
        Index("idx_analog_attribute_composite", "analog_id", "attribute_id"),
    )

    def __str__(self) -> str:
        return f"AnalogAttribute {self.id}: Analog={self.analog_id}, Attribute={self.attribute_id}"
