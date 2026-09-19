from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services.cache_service import check_cache, add_to_cache
from app.services.rag_client import ask_rag

router = APIRouter(prefix="/questions", tags=["questions"])


@router.post("/ask", response_model=schemas.AnswerOut)
async def ask_question(payload: schemas.QuestionIn, db: Session = Depends(get_db)):
    # 1. Validate active session
    session = (
        db.query(models.ClassroomSession)
        .filter_by(id=payload.session_id, status="active")
        .first()
    )
    if not session:
        raise HTTPException(status_code=400, detail="No active session found")

    # 2. Validate subject exists
    subject = db.query(models.Subject).filter_by(id=payload.subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    # 3. Persist the question first
    question = models.Question(
        session_id=payload.session_id,
        student_id=payload.student_id,
        subject_id=payload.subject_id,
        text=payload.text,
        language=payload.language,
    )
    db.add(question)
    db.commit()
    db.refresh(question)

    # 4. Check semantic/exact cache first
    cached_entry = check_cache(db, payload.text, payload.subject_id)

    if cached_entry:
        answer_text = cached_entry.answer_text
        result = {
            "answer": answer_text,
            "language": payload.language,
            "style": "cached",
            "verified": True,
            "verification_status": "verified",
            "sources": [],
            "cached": True,
        }
    else:
        # 5. Cache miss -> call RAG/LLM service
        rag_result = await ask_rag(payload.text, payload.subject_id, payload.language)
        result = {
            "answer": rag_result["answer"],
            "language": rag_result.get("language", payload.language),
            "style": rag_result.get("style", "explanatory"),
            "verified": rag_result.get("verified", False),
            "verification_status": rag_result.get("verification_status", "pending"),
            "sources": rag_result.get("sources", []),
            "cached": False,
        }

    # 6. Persist the answer
    answer = models.Answer(
        question_id=question.id,
        answer_text=result["answer"],
        verified=result["verified"],
        verification_status=result["verification_status"],
        cached=result["cached"],
        status="pending",  # awaiting teacher approval (Phase 6)
    )
    db.add(answer)
    db.commit()
    db.refresh(answer)

    return {
        "question_id": question.id,
        "answer": result["answer"],
        "language": result["language"],
        "style": result["style"],
        "verified": result["verified"],
        "verification_status": result["verification_status"],
        "sources": result["sources"],
        "cached": result["cached"],
    }


@router.get("/")
def list_questions(db: Session = Depends(get_db)):
    questions = db.query(models.Question).all()
    return [
        {
            "id": q.id,
            "session_id": q.session_id,
            "student_id": q.student_id,
            "subject_id": q.subject_id,
            "text": q.text,
            "language": q.language,
            "created_at": q.created_at,
        }
        for q in questions
    ]


@router.get("/{question_id}/answer")
def get_answer(question_id: int, db: Session = Depends(get_db)):
    answer = db.query(models.Answer).filter_by(question_id=question_id).first()
    if not answer:
        raise HTTPException(status_code=404, detail="Answer not found")
    return {
        "id": answer.id,
        "question_id": answer.question_id,
        "answer_text": answer.answer_text,
        "verified": answer.verified,
        "verification_status": answer.verification_status,
        "cached": answer.cached,
        "status": answer.status,
    }