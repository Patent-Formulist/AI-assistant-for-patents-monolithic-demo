from sqlalchemy import JSON, BigInteger, Column, DateTime, ForeignKey, String, Text
from sqlalchemy.sql import func

from core.db.db import Base


class LegalConsentModel(Base):
    """A user accepted a version of a legal document: append-only evidence.

    The latest row per document wins (a user may change cookie choices).
    """

    __tablename__ = "legal_consents"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(
        BigInteger, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    document = Column(String(50), nullable=False)
    version = Column(String(50), nullable=False)
    # Optional choices within the document, e.g. cookie categories
    choices = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    accepted_at = Column(DateTime, server_default=func.now(), nullable=False)
