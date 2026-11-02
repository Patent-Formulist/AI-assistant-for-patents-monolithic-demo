from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Column, ForeignKey, Index, UniqueConstraint
from sqlalchemy.orm import relationship

from core.db.db import Base
from core.db.mixins import SoftDeleteMixin, TimestampMixin

if TYPE_CHECKING:
    pass


class PatentAttributeModel(Base, TimestampMixin, SoftDeleteMixin):
    """Модель для связи аналогов с атрибутами"""

    __tablename__ = "patent_attributes"
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    patent_id = Column(
        BigInteger,
        ForeignKey("patent.id", ondelete="CASCADE", name="fk_patent_attribute_patent_id"),
        nullable=False,
        comment="ID патента",
    )
    attribute_id = Column(
        BigInteger,
        ForeignKey("attributes.id", ondelete="CASCADE", name="fk_patent_attribute_attribute_id"),
        nullable=False,
        comment="ID атрибута",
    )
    patent = relationship("PatentModel", back_populates="patent_attributes", lazy="joined")
    attribute = relationship("AttributeModel", back_populates="patent_attributes", lazy="joined")
    __table_args__ = (
        # Уникальность пары патент-атрибут
        UniqueConstraint("patent_id", "attribute_id", name="uq_patent_attribute"),
        # Индексы для ускорения поиска
        Index("idx_patent_attribute_patent_id", "patent_id"),
        Index("idx_patent_attribute_attribute_id", "attribute_id"),
        Index("idx_patent_attribute_composite", "patent_id", "attribute_id"),
    )
