from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from core.db.db import Base
from core.db.mixins import SoftDeleteMixin, TimestampMixin
from core.db.types import GUID


class KeyUsageModel(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "key_usage"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    key_id = Column(
        GUID,
        ForeignKey("key.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID ключа",
    )
    used = Column(Integer, nullable=False, default=0, comment="Количество использований")
    limit = Column(
        Integer,
        nullable=False,
        default=5,
        comment="Максимальное количество использований",
    )
    reset_time = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Время, когда сбрасывается счётчик использований",
    )

    key = relationship("KeyModel", back_populates="usages")
