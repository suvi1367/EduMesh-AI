import os
import json
from datetime import datetime, timezone
from typing import Generator
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, Boolean, DateTime, JSON
from sqlalchemy.orm import sessionmaker, declarative_base

# Database file location
DB_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(DB_DIR, exist_ok=True)
DATABASE_URL = os.getenv("EDUMESH_DATABASE_URL", f"sqlite:///{os.path.join(DB_DIR, 'edumesh.db')}")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def utc_now():
    return datetime.now(timezone.utc)


class SemanticCacheEntry(Base):
    __tablename__ = "semantic_cache_entries"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False, index=True)
    embedding = Column(JSON, nullable=False)  # List[float]
    answer = Column(Text, nullable=False)
    evidence_metadata = Column(JSON, nullable=True, default=dict)
    subject = Column(String(50), nullable=True, index=True)
    class_grade = Column(String(50), nullable=True, index=True)
    language = Column(String(20), nullable=True, index=True)
    curriculum = Column(String(100), nullable=True)
    approved = Column(Boolean, default=False, nullable=False, index=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    last_used_at = Column(DateTime, default=utc_now, nullable=False)
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
            "response_latency_ms": self.response_latency_ms
        }


class SyncHistoryEntry(Base):
    __tablename__ = "sync_history"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=utc_now, nullable=False)
    sync_type = Column(String(50), nullable=False)  # e.g., "manual_check", "auto_check", "installation"
    status = Column(String(20), nullable=False)    # e.g., "success", "offline", "error"
    details = Column(Text, nullable=True)
    updates_applied = Column(JSON, nullable=True, default=list)

    def to_dict(self):
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "sync_type": self.sync_type,
            "status": self.status,
            "details": self.details,
            "updates_applied": self.updates_applied or []
        }


def init_db():
    """Safely create all tables if they do not exist."""
    Base.metadata.create_all(bind=engine)


def get_db() -> Generator:
    """FastAPI dependency for database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
