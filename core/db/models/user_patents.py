from sqlalchemy import (
    BigInteger,
    Column,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from core.db.db import Base
from core.db.mixins import SoftDeleteMixin, TimestampMixin


class UserPatentModel(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "user_patent"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="Уникальный ID связи")
    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID пользователя",
    )
    patent_id = Column(
        BigInteger,
        ForeignKey("patent.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID патента",
    )

    # Последняя открытая секция страницы патента (после reload и на другом устройстве).
    # Значения: core.enum.ui_button.UIButton. Прогресс пайплайнов берётся из jobs (ADR 0004).
    last_ui_button = Column(
        String(32),
        nullable=False,
        server_default="ANALOGS_SEARCH",
        comment="Last UI button for patent progress",
    )

    __table_args__ = (UniqueConstraint("user_id", "patent_id", name="uq_user_patent"),)
    patent = relationship("PatentModel", back_populates="user_patents", lazy="joined")
    user = relationship("UserModel", back_populates="user_patents", lazy="joined")

    def __repr__(self):
        return f"UserPatent(id={self.id}, user_id={self.user_id}, patent_id={self.patent_id})"
