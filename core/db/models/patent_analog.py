from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Column, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship

from core.db.db import Base
from core.db.mixins import SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    pass


class PatentAnalogModel(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "patent_analog"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="Уникальный ID связи")

    analog_id = Column(
        BigInteger,
        ForeignKey("analog.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID аналога",
    )
    patent_id = Column(
        BigInteger,
        ForeignKey("patent.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID патента",
    )

    patent = relationship("PatentModel", back_populates="patent_analogs")
    analog = relationship("AnalogModel", back_populates="patent_analogs")

    __table_args__ = (
        UniqueConstraint("analog_id", "patent_id", name="uq_patent_analog"),
        Index("idx_analog_patent", "analog_id", "patent_id"),
    )

    def __repr__(self):
        return f"PatentAnalog(id={self.id}, analog_id={self.analog_id}, patent_id={self.patent_id}"
