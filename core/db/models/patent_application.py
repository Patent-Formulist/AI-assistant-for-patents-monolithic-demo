from sqlalchemy import JSON, BigInteger, Boolean, Column, DateTime, ForeignKey, Text, false

from core.db.db import Base
from core.db.mixins import TimestampMixin


class PatentApplicationModel(Base, TimestampMixin):
    __tablename__ = "patent_application"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    patent_id = Column(
        BigInteger,
        ForeignKey("patent.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        comment="ID патента",
    )
    abstract = Column(Text, nullable=True, comment="Реферат")
    claims = Column(JSON, nullable=True, comment="Формула изобретения (список пунктов)")
    description = Column(Text, nullable=True, comment="Описание изобретения")
    generated_at = Column(DateTime, nullable=True, comment="Дата последней генерации")
    # Set when the patent data the document was generated from changes.
    # Server default and comment match the initial migration.
    is_outdated = Column(
        Boolean,
        nullable=False,
        default=False,
        server_default=false(),
        comment="Устарел ли документ",
    )

    def __repr__(self) -> str:
        return f"PatentApplication(patent_id={self.patent_id}, generated_at={self.generated_at})"
