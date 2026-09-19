from sqlalchemy.orm import Session
from app import models


def check_cache(db: Session, question_text: str, subject_id: int):
    """
    Naive exact-match cache lookup for the prototype.
    Can be upgraded later to semantic/similarity matching.
    """
    return (
        db.query(models.CacheEntry)
        .filter_by(subject_id=subject_id, question_text=question_text)
        .first()
    )


def add_to_cache(db: Session, question_text: str, answer_text: str, subject_id: int):
    entry = models.CacheEntry(
        subject_id=subject_id,
        question_text=question_text,
        answer_text=answer_text,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry