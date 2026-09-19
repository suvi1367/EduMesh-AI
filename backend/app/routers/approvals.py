from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services.cache_service import add_to_cache

router = APIRouter(prefix="/answers", tags=["approvals"])


@router.post("/{answer_id}/approve")
def approve_answer(answer_id: int, db: Session = Depends(get_db)):
    answer = db.query(models.Answer).filter_by(id=answer_id).first()
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")

    answer.status = "approved"
    db.commit()
    db.refresh(answer)

    # Save into approved_answers table
    approved = models.ApprovedAnswer(
        answer_id=answer.id,
        question_id=answer.question_id,
        text=answer.answer_text,
    )
    db.add(approved)
    db.commit()
    db.refresh(approved)

    # Only approved knowledge becomes eligible for the shared cache
    question = db.query(models.Question).filter_by(id=answer.question_id).first()
    if question:
        add_to_cache(db, question.text, answer.answer_text, question.subject_id)

    return {
        "id": approved.id,
        "question_id": approved.question_id,
        "answer_id": approved.answer_id,
        "status": "approved",
    }


@router.post("/{answer_id}/correct")
def correct_answer(answer_id: int, payload: schemas.CorrectionIn, db: Session = Depends(get_db)):
    answer = db.query(models.Answer).filter_by(id=answer_id).first()
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")

    # Save the corrected text as the new answer text, and approve it
    answer.answer_text = payload.corrected_text
    answer.status = "approved"
    answer.verified = True
    answer.verification_status = "verified"
    db.commit()
    db.refresh(answer)

    approved = models.ApprovedAnswer(
        answer_id=answer.id,
        question_id=answer.question_id,
        text=answer.answer_text,
    )
    db.add(approved)
    db.commit()
    db.refresh(approved)

    question = db.query(models.Question).filter_by(id=answer.question_id).first()
    if question:
        add_to_cache(db, question.text, answer.answer_text, question.subject_id)

    return {
        "id": approved.id,
        "question_id": approved.question_id,
        "answer_id": approved.answer_id,
        "status": "approved (corrected)",
    }


@router.post("/{answer_id}/reject")
def reject_answer(answer_id: int, db: Session = Depends(get_db)):
    answer = db.query(models.Answer).filter_by(id=answer_id).first()
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")

    answer.status = "rejected"
    db.commit()
    db.refresh(answer)

    return {"id": answer.id, "status": "rejected"}


@router.get("/pending")
def list_pending_answers(db: Session = Depends(get_db)):
    answers = db.query(models.Answer).filter_by(status="pending").all()
    return [
        {
            "id": a.id,
            "question_id": a.question_id,
            "answer_text": a.answer_text,
            "verified": a.verified,
            "verification_status": a.verification_status,
        }
        for a in answers
    ]