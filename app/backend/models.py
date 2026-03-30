from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255))
    picture = Column(Text)
    provider = Column(String(50), default="google")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, default=datetime.utcnow)
    transcripts = relationship("Transcript", back_populates="user", cascade="all, delete-orphan")
    history = relationship("History", back_populates="user", cascade="all, delete-orphan")


class Transcript(Base):
    __tablename__ = "transcripts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255))
    file_type = Column(String(20))
    program_detected = Column(String(50))
    level_used = Column(Integer, default=3)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    raw_data = Column(JSON)
    user = relationship("User", back_populates="transcripts")
    courses = relationship("CourseRecord", back_populates="transcript", cascade="all, delete-orphan")
    audit_result = relationship("AuditResult", back_populates="transcript", uselist=False, cascade="all, delete-orphan")
    history = relationship("History", back_populates="transcript", cascade="all, delete-orphan")


class CourseRecord(Base):
    __tablename__ = "course_records"
    id = Column(Integer, primary_key=True, autoincrement=True)
    transcript_id = Column(Integer, ForeignKey("transcripts.id"), nullable=False)
    course_code = Column(String(20), nullable=False)
    course_title = Column(String(255))
    credits = Column(Float, default=0.0)
    grade = Column(String(5))
    semester = Column(String(20))
    year = Column(Integer)
    attempt = Column(Integer, default=1)
    is_valid_nsu = Column(Integer, default=1)
    transcript = relationship("Transcript", back_populates="courses")


class AuditResult(Base):
    __tablename__ = "audit_results"
    id = Column(Integer, primary_key=True, autoincrement=True)
    transcript_id = Column(Integer, ForeignKey("transcripts.id"), nullable=False, unique=True)
    cgpa = Column(Float, default=0.0)
    total_quality_points = Column(Float, default=0.0)
    credits_attempted = Column(Float, default=0.0)
    credits_earned = Column(Float, default=0.0)
    failed_credits = Column(Float, default=0.0)
    withdrawn_credits = Column(Float, default=0.0)
    incomplete_credits = Column(Float, default=0.0)
    academic_standing = Column(String(50))
    program = Column(String(50))
    major = Column(String(100))
    total_required = Column(Integer, default=130)
    credits_remaining = Column(Float, default=0.0)
    progress_percent = Column(Float, default=0.0)
    estimated_semesters = Column(Integer, default=0)
    waiver_status = Column(JSON)
    missing_courses = Column(JSON)
    category_progress = Column(JSON)
    invalid_courses = Column(JSON)
    retake_history = Column(JSON)
    result_data = Column(JSON)
    computed_at = Column(DateTime, default=datetime.utcnow)
    transcript = relationship("Transcript", back_populates="audit_result")


class History(Base):
    __tablename__ = "history"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    transcript_id = Column(Integer, ForeignKey("transcripts.id"), nullable=True)
    action = Column(String(50), default="audit")
    filename = Column(String(255))
    program = Column(String(50))
    level_used = Column(Integer, default=3)
    cgpa = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="history")
    transcript = relationship("Transcript", back_populates="history")
