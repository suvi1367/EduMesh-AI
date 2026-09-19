from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from app.services.auth_service import hash_password, verify_password

router = APIRouter(tags=["auth"])


@router.post("/signup", response_model=schemas.LoginResponse)
def signup(payload: schemas.TeacherSignup, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter_by(username=payload.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")

    user = models.User(
        username=payload.username,
        password_hash=hash_password(payload.password),
        role="teacher",
        institution_id=payload.institution_id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    teacher = models.Teacher(
        user_id=user.id,
        full_name=payload.full_name,
        institution_id=payload.institution_id,
    )
    db.add(teacher)
    db.commit()
    db.refresh(teacher)

    return {
        "teacher_id": teacher.id,
        "username": user.username,
        "full_name": teacher.full_name,
        "message": "Signup successful",
    }


@router.post("/login", response_model=schemas.LoginResponse)
def login(payload: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter_by(username=payload.username).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    teacher = db.query(models.Teacher).filter_by(user_id=user.id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Teacher profile not found for this user")

    return {
        "teacher_id": teacher.id,
        "username": user.username,
        "full_name": teacher.full_name,
        "message": "Login successful",
    }