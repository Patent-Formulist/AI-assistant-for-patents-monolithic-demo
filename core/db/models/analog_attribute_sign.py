from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from core.db.db import Base
from core.db.mixins import SoftDeleteMixin, TimestampMixin


class AnalogAttributeSignModel(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "analog_attribute_sign"
    __table_args__ = (PrimaryKeyConstraint("attribute_id", "analog_id"),)

    attribute_id = Column(
        BigInteger, ForeignKey("attributes.id", ondelete="CASCADE"), nullable=False
    )
    analog_id = Column(BigInteger, ForeignKey("analog.id", ondelete="CASCADE"), nullable=False)
    sign = Column(Boolean, nullable=False)

    analog = relationship("AnalogModel", backref="attribute_signs")
    attribute = relationship("AttributeModel", backref="analog_signs")
