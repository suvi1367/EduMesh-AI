from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/classrooms", tags=["classrooms"])


@router.post("/start", response_model=schemas.SessionOut)
def start_session(payload: schemas.SessionCreate, db: Session = Depends(get_db)):
    session = models.ClassroomSession(
        class_id=payload.class_id,
        teacher_id=payload.teacher_id,
        status="active"
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.post("/{session_id}/join")
def join_session(session_id: int, student_id: int, db: Session = Depends(get_db)):
    session = db.query(models.ClassroomSession).filter_by(id=session_id, status="active").first()
    if not session:
        raise HTTPException(status_code=404, detail="Active session not found")
    student = db.query(models.Student).filter_by(id=student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    existing = db.query(models.SessionParticipant).filter_by(
        session_id=session_id, student_id=student_id
    ).first()
    if not existing:
        participant = models.SessionParticipant(session_id=session_id, student_id=student_id)
        db.add(participant)
        db.commit()

    return {"message": "joined", "session_id": session_id, "student_id": student_id}


@router.get("/{session_id}/students")
def list_students(session_id: int, db: Session = Depends(get_db)):
    session = db.query(models.ClassroomSession).filter_by(id=session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    participants = (
        db.query(models.Student)
        .join(models.SessionParticipant, models.SessionParticipant.student_id == models.Student.id)
        .filter(models.SessionParticipant.session_id == session_id)
        .all()
    )
    return [{"id": s.id, "full_name": s.full_name} for s in participants]

@router.post("/{session_id}/end", response_model=schemas.SessionOut)
def end_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(models.ClassroomSession).filter_by(id=session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session.status = "ended"
    from datetime import datetime, timezone
    session.ended_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(session)
    return session