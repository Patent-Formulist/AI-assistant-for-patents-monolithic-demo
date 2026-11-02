from sqlalchemy import (
    JSON,
    BigInteger,
    Column,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship

from core.db.db import Base
from core.db.mixins import TimestampMixin
from core.enum.job_status import JobStatus
from core.enum.job_type import JobType


class JobModel(Base, TimestampMixin):
    __tablename__ = "jobs"
    __table_args__ = (Index("ix_jobs_patent_type_id", "patent_id", "job_type", "id"),)

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    patent_id = Column(BigInteger, ForeignKey("patent.id", ondelete="CASCADE"), nullable=False)
    job_type = Column(SQLEnum(JobType), nullable=False)
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING)
    current_stage = Column(String(50), nullable=True)
    error = Column(Text, nullable=True)
    result = Column(JSON, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    tasks = relationship("TaskModel", back_populates="job", cascade="all, delete-orphan")
    patent = relationship("PatentModel")
