from sqlalchemy import BigInteger, Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import relationship

from core.db.db import Base
from core.db.mixins import SoftDeleteMixin, TimestampMixin
from core.db.types import GUID


class UserTokenModel(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "user_token"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="Уникальный ID связи")
    user_id = Column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID пользователя",
    )
    token_id = Column(
        GUID,
        ForeignKey("tokens.jti", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID токена (JTI)",
    )

    __table_args__ = (UniqueConstraint("user_id", "token_id", name="uq_user_token"),)

    token = relationship("TokenModel", back_populates="user_tokens")
    user = relationship("UserModel", back_populates="user_tokens")
