from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from core.db.db import Base
from core.db.types import GUID


class LLMUsageModel(Base):
    """Tokens of one LLM response; append-only, what the provider billed us.

    Kept for failed steps too (``succeeded``): the provider bills every
    response. References are SET NULL so deleting a patent or a job keeps
    the record.
    """

    __tablename__ = "llm_usage"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=True, index=True, comment="Чья работа")
    patent_id = Column(BigInteger, ForeignKey("patent.id", ondelete="SET NULL"), nullable=True)
    job_id = Column(
        BigInteger, ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True, index=True
    )
    task_id = Column(BigInteger, ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)
    step = Column(String(100), nullable=False, comment="Имя задачи пайплайна")
    attempt = Column(Integer, nullable=False, comment="Попытка шага в Temporal")
    succeeded = Column(Boolean, nullable=False, comment="Успешна ли попытка шага")
    model = Column(String(100), nullable=False)
    key_id = Column(GUID, ForeignKey("key.id", ondelete="SET NULL"), nullable=True)
    prompt_tokens = Column(Integer, nullable=False)
    completion_tokens = Column(Integer, nullable=False)
    cached_tokens = Column(Integer, nullable=False, default=0, comment="Из кэша провайдера")
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
