from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime, Boolean, Text,Float, JSON
)
from sqlalchemy.sql import func
from app.database import Base


class Institution(Base):
    __tablename__ = "institutions"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    institution_id = Column(Integer, ForeignKey("institutions.id"))
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)  # "teacher" or "student"
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    full_name = Column(String, nullable=False)
    institution_id = Column(Integer, ForeignKey("institutions.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Class(Base):
    __tablename__ = "classes"
    id = Column(Integer, primary_key=True)
    institution_id = Column(Integer, ForeignKey("institutions.id"))
    name = Column(String, nullable=False)   # e.g. "Grade 6 - Section A"
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Subject(Base):
    __tablename__ = "subjects"
    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey("classes.id"))
    name = Column(String, nullable=False)   # e.g. "Science"
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    full_name = Column(String, nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Document(Base):
    __tablename__ = "documents"
    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    file_path = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    status = Column(String, default="uploaded")  # uploaded/processing/indexed/failed
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())


class ClassroomSession(Base):
    __tablename__ = "classroom_sessions"
    id = Column(Integer, primary_key=True)
    class_id = Column(Integer, ForeignKey("classes.id"))
    teacher_id = Column(Integer, ForeignKey("teachers.id"))
    status = Column(String, default="active")  # active/ended
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)

class SessionParticipant(Base):
    __tablename__ = "session_participants"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("classroom_sessions.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    joined_at = Column(DateTime(timezone=True), server_default=func.now())


class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("classroom_sessions.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    text = Column(Text, nullable=False)
    language = Column(String, default="en")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Answer(Base):
    __tablename__ = "answers"
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    answer_text = Column(Text, nullable=False)
    verified = Column(Boolean, default=False)
    verification_status = Column(String, default="pending")  # pending/verified/failed
    cached = Column(Boolean, default=False)
    status = Column(String, default="pending")  # pending/approved/rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ApprovedAnswer(Base):
    __tablename__ = "approved_answers"
    id = Column(Integer, primary_key=True)
    answer_id = Column(Integer, ForeignKey("answers.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    text = Column(Text, nullable=False)
    approved_at = Column(DateTime(timezone=True), server_default=func.now())


class CacheEntry(Base):
    __tablename__ = "cache_entries"
    id = Column(Integer, primary_key=True)
    subject_id = Column(Integer, ForeignKey("subjects.id"))
    question_text = Column(Text, nullable=False)
    answer_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SyncHistory(Base):
    __tablename__ = "sync_history"
    id = Column(Integer, primary_key=True)
    institution_id = Column(Integer, ForeignKey("institutions.id"))
    sync_type = Column(String, nullable=False)  # e.g. "cache_sync", "content_sync"
    status = Column(String, default="pending")  # pending/success/failed
    synced_at = Column(DateTime(timezone=True), server_default=func.now())

class SemanticCacheEntry(Base):
    __tablename__ = "semantic_cache_entries"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False, index=True)
    embedding = Column(JSON, nullable=False)
    answer = Column(Text, nullable=False)
    evidence_metadata = Column(JSON, nullable=True, default=dict)
    subject = Column(String(50), nullable=True, index=True)
    class_grade = Column(String(50), nullable=True, index=True)
    language = Column(String(20), nullable=True, index=True)
    curriculum = Column(String(100), nullable=True)
    approved = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True), server_default=func.now())
    hit_count = Column(Integer, default=0, nullable=False)
    response_latency_ms = Column(Float, nullable=True, default=0.0)

    def to_dict(self):
        return {
            "id": self.id,
            "question": self.question,
            "answer": self.answer,
            "evidence_metadata": self.evidence_metadata or {},
            "subject": self.subject,
            "class_grade": self.class_grade,
            "language": self.language,
            "curriculum": self.curriculum,
            "approved": self.approved,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_used_at": self.last_used_at.isoformat() if self.last_used_at else None,
            "hit_count": self.hit_count,
            "response_latency_ms": self.response_latency_ms,
        }


class SyncHistoryEntry(Base):
    __tablename__ = "sync_history_log"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    sync_type = Column(String(50), nullable=False)
    status = Column(String(20), nullable=False)
    details = Column(Text, nullable=True)
    updates_applied = Column(JSON, nullable=True, default=list)

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "sync_type": self.sync_type,
            "status": self.status,
            "details": self.details,
            "updates_applied": self.updates_applied or [],
        }