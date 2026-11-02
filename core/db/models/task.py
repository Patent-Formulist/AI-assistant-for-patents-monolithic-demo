from sqlalchemy import (
    JSON,
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship

from core.db.db import Base
from core.db.mixins import TimestampMixin
from core.enum.task_status import TaskStatus


class TaskModel(Base, TimestampMixin):
    __tablename__ = "tasks"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    job_id = Column(BigInteger, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(100), nullable=False)
    order = Column(Integer, nullable=False)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING)
    progress = Column(Integer, default=0)
    error = Column(Text, nullable=True)
    result = Column(JSON, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    meta = Column(JSON, nullable=True)

    job = relationship("JobModel", back_populates="tasks")
