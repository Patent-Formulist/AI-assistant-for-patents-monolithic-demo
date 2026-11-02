from sqlalchemy import BigInteger, Column, ForeignKey, Index, text
from sqlalchemy.orm import relationship

from core.db.db import Base
from core.db.mixins import SoftDeleteMixin, TimestampMixin


class IdentifyAttributeModel(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "identify_attribute"
    __table_args__ = (
        Index(
            "uq_identify_attribute_active_unique",
            "patent_id",
            "analog_id",
            "analog_attribute_id",
            "patent_attribute_id",
            "general_attribute_id",
            unique=True,
            postgresql_where=text("is_active = true"),
        ),
        Index(
            "uq_identify_attribute_deleted_unique",
            "patent_id",
            "analog_id",
            "analog_attribute_id",
            "patent_attribute_id",
            "general_attribute_id",
            "deleted_at",
            unique=True,
            postgresql_where=text("is_active = false"),
        ),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    patent_id = Column(BigInteger, ForeignKey("patent.id"), nullable=False)
    analog_id = Column(BigInteger, ForeignKey("analog.id"), nullable=False)
    analog_attribute_id = Column(
        BigInteger, ForeignKey("attributes.id", ondelete="CASCADE"), nullable=True
    )
    patent_attribute_id = Column(
        BigInteger, ForeignKey("attributes.id", ondelete="CASCADE"), nullable=True
    )
    general_attribute_id = Column(
        BigInteger, ForeignKey("attributes.id", ondelete="CASCADE"), nullable=False
    )

    patent = relationship(
        "PatentModel",
        foreign_keys="IdentifyAttributeModel.patent_id",
        back_populates="identify_attributes",
    )

    analog = relationship(
        "AnalogModel",
        foreign_keys="IdentifyAttributeModel.analog_id",
        back_populates="identify_attributes",
    )

    analog_attribute = relationship(
        "AttributeModel",
        foreign_keys="IdentifyAttributeModel.analog_attribute_id",
        back_populates="identify_attributes_as_analog",
    )

    patent_attribute = relationship(
        "AttributeModel",
        foreign_keys="IdentifyAttributeModel.patent_attribute_id",
        back_populates="identify_attributes_as_patent",
    )

    general_attribute = relationship(
        "AttributeModel",
        foreign_keys="IdentifyAttributeModel.general_attribute_id",
        back_populates="identify_attributes_as_general",
    )
