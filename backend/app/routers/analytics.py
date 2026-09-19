from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app import models

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/session/{session_id}")
def session_analytics(session_id: int, db: Session = Depends(get_db)):
    session = db.query(models.ClassroomSession).filter_by(id=session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    total_questions = db.query(models.Question).filter_by(session_id=session_id).count()

    unique_questions = (
        db.query(models.Question.text)
        .filter_by(session_id=session_id)
        .distinct()
        .count()
    )

    connected_students = (
        db.query(models.Question.student_id)
        .filter_by(session_id=session_id)
        .distinct()
        .count()
    )

    review_queue = (
        db.query(models.Answer)
        .join(models.Question, models.Answer.question_id == models.Question.id)
        .filter(models.Question.session_id == session_id, models.Answer.status == "pending")
        .count()
    )

    return {
        "session_id": session_id,
        "connected_students": connected_students,
        "total_questions": total_questions,
        "unique_questions": unique_questions,
        "review_queue": review_queue,
    }


@router.get("/subject/{subject_id}/frequent-topics")
def frequent_topics(subject_id: int, db: Session = Depends(get_db)):
    results = (
        db.query(models.Question.text, func.count(models.Question.id).label("count"))
        .filter_by(subject_id=subject_id)
        .group_by(models.Question.text)
        .order_by(func.count(models.Question.id).desc())
        .limit(10)
        .all()
    )
    return [{"question_text": r[0], "count": r[1]} for r in results]


@router.get("/institution/{institution_id}/overview")
def institution_overview(institution_id: int, db: Session = Depends(get_db)):
    institution = db.query(models.Institution).filter_by(id=institution_id).first()
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")

    class_ids = [c.id for c in db.query(models.Class).filter_by(institution_id=institution_id).all()]
    subject_ids = [s.id for s in db.query(models.Subject).filter(models.Subject.class_id.in_(class_ids)).all()]

    total_questions = (
        db.query(models.Question).filter(models.Question.subject_id.in_(subject_ids)).count()
        if subject_ids else 0
    )
    total_documents = (
        db.query(models.Document).filter(models.Document.subject_id.in_(subject_ids)).count()
        if subject_ids else 0
    )

    return {
        "institution_id": institution_id,
        "total_classes": len(class_ids),
        "total_subjects": len(subject_ids),
        "total_questions": total_questions,
        "total_documents": total_documents,
    }