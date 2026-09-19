from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/institutions", tags=["institutions"])


@router.post("/", response_model=schemas.InstitutionOut)
def create_institution(payload: schemas.InstitutionCreate, db: Session = Depends(get_db)):
    inst = models.Institution(name=payload.name)
    db.add(inst)
    db.commit()
    db.refresh(inst)
    return inst


@router.get("/", response_model=list[schemas.InstitutionOut])
def list_institutions(db: Session = Depends(get_db)):
    return db.query(models.Institution).all()


@router.get("/{institution_id}", response_model=schemas.InstitutionOut)
def get_institution(institution_id: int, db: Session = Depends(get_db)):
    inst = db.query(models.Institution).filter_by(id=institution_id).first()
    if not inst:
        raise HTTPException(status_code=404, detail="Institution not found")
    return inst


# ---- Classes ----
@router.post("/classes", response_model=schemas.ClassOut)
def create_class(payload: schemas.ClassCreate, db: Session = Depends(get_db)):
    cls = models.Class(institution_id=payload.institution_id, name=payload.name)
    db.add(cls)
    db.commit()
    db.refresh(cls)
    return cls


@router.get("/classes/{class_id}", response_model=schemas.ClassOut)
def get_class(class_id: int, db: Session = Depends(get_db)):
    cls = db.query(models.Class).filter_by(id=class_id).first()
    if not cls:
        raise HTTPException(status_code=404, detail="Class not found")
    return cls


# ---- Subjects ----
@router.post("/subjects", response_model=schemas.SubjectOut)
def create_subject(payload: schemas.SubjectCreate, db: Session = Depends(get_db)):
    subj = models.Subject(class_id=payload.class_id, name=payload.name)
    db.add(subj)
    db.commit()
    db.refresh(subj)
    return subj


@router.get("/subjects/{subject_id}", response_model=schemas.SubjectOut)
def get_subject(subject_id: int, db: Session = Depends(get_db)):
    subj = db.query(models.Subject).filter_by(id=subject_id).first()
    if not subj:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subj