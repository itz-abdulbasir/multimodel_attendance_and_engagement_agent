"""
Multimodal Attendance & Engagement Agent - SQLAlchemy Declarative Models
Epic 1 & Data Storage Layer: Structured ORM Models for Classroom Analytics
"""

import os
from datetime import datetime
from typing import Generator

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Boolean,
    ForeignKey,
    Text
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session

Base = declarative_base()

class StudentModel(Base):
    __tablename__ = "students"

    id = Column(String(32), primary_key=True)
    pseudonym_hash = Column(String(64), nullable=False, unique=True)
    display_name = Column(String(128), nullable=False)
    seat_label = Column(String(64), default="Desk")
    created_at = Column(DateTime, default=datetime.utcnow)

    attendance_records = relationship("AttendanceLogModel", back_populates="student")


class SessionModel(Base):
    __tablename__ = "sessions"

    id = Column(String(64), primary_key=True)
    course_name = Column(String(128), nullable=False)
    instructor_name = Column(String(128), nullable=False)
    start_time = Column(String(64), nullable=False)
    end_time = Column(String(64), nullable=True)
    status = Column(String(32), default="ACTIVE")
    total_enrolled = Column(Integer, default=10)
    total_present = Column(Integer, default=0)

    attendance_logs = relationship("AttendanceLogModel", back_populates="session")
    engagement_intervals = relationship("EngagementIntervalModel", back_populates="session")
    suggestions = relationship("TeachingSuggestionModel", back_populates="session")


class AttendanceLogModel(Base):
    __tablename__ = "attendance_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("sessions.id"), nullable=False)
    student_id = Column(String(32), ForeignKey("students.id"), nullable=False)
    first_detected_at = Column(String(64), nullable=False)
    last_detected_at = Column(String(64), nullable=False)
    total_active_seconds = Column(Float, default=0.0)
    presence_ratio = Column(Float, default=0.0)
    status = Column(String(32), default="CANDIDATE")
    verification_hash = Column(String(64), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("SessionModel", back_populates="attendance_logs")
    student = relationship("StudentModel", back_populates="attendance_records")


class EngagementIntervalModel(Base):
    __tablename__ = "engagement_intervals"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("sessions.id"), nullable=False)
    timestamp = Column(String(64), nullable=False)
    epoch_seconds = Column(Float, nullable=False)
    visual_attention_score = Column(Float, nullable=False)
    motion_energy_score = Column(Float, nullable=False)
    audio_energy_score = Column(Float, nullable=False)
    audio_rhythm_mode = Column(String(64), nullable=False)
    overall_engagement_index = Column(Float, nullable=False)
    active_participants = Column(Integer, default=0)

    session = relationship("SessionModel", back_populates="engagement_intervals")


class TeachingSuggestionModel(Base):
    __tablename__ = "teaching_suggestions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(64), ForeignKey("sessions.id"), nullable=False)
    timestamp = Column(String(64), nullable=False)
    alert_level = Column(String(32), nullable=False) # 'INFO', 'ADVISORY', 'ACTIONABLE'
    title = Column(String(128), nullable=False)
    reason = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=False)
    context_metadata = Column(Text, nullable=True)

    session = relationship("SessionModel", back_populates="suggestions")


# Engine and session factory helper
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "classroom_intelligence.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session() -> Generator[Session, None, None]:
    """Dependency helper for FastAPI endpoints or standalone ORM access."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
