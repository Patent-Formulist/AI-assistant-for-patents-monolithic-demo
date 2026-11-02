from sqlalchemy import BigInteger, Boolean, Column, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from core.db.db import Base
from core.db.mixins import SoftDeleteMixin, TimestampMixin


class PatentAttributeSignModel(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "patent_attribute_sign"
    __table_args__ = (PrimaryKeyConstraint("attribute_id", "patent_id"),)

    attribute_id = Column(
        BigInteger, ForeignKey("attributes.id", ondelete="CASCADE"), nullable=False
    )
    patent_id = Column(BigInteger, ForeignKey("patent.id", ondelete="CASCADE"), nullable=False)
    sign = Column(Boolean, nullable=False)

    patent = relationship("PatentModel", backref="attribute_signs")
    attribute = relationship("AttributeModel", backref="patent_signs")
