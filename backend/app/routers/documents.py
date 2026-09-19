import os
import shutil
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app import models

router = APIRouter(prefix="/documents", tags=["documents"])

ALLOWED_EXTENSIONS = {".pdf"}


@router.post("/upload")
async def upload_document(
    subject_id: int = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    # Validate subject exists
    subject = db.query(models.Subject).filter_by(id=subject_id).first()
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    # Validate file extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Ensure docs folder exists
    os.makedirs(settings.DOCS_DIR, exist_ok=True)

    # Build a safe save path
    save_path = os.path.join(settings.DOCS_DIR, file.filename)

    # Validate file size while saving
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    total_size = 0
    with open(save_path, "wb") as out_file:
        while chunk := await file.read(1024 * 1024):
            total_size += len(chunk)
            if total_size > max_bytes:
                out_file.close()
                os.remove(save_path)
                raise HTTPException(
                    status_code=400,
                    detail=f"File exceeds max size of {settings.MAX_UPLOAD_MB} MB"
                )
            out_file.write(chunk)

    # Create the document record (store PATH, not the file itself)
    doc = models.Document(
        subject_id=subject_id,
        file_path=save_path,
        original_filename=file.filename,
        status="uploaded",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {
        "id": doc.id,
        "subject_id": doc.subject_id,
        "original_filename": doc.original_filename,
        "status": doc.status,
        "uploaded_at": doc.uploaded_at,
    }


@router.get("/{document_id}/status")
def get_document_status(document_id: int, db: Session = Depends(get_db)):
    doc = db.query(models.Document).filter_by(id=document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"id": doc.id, "status": doc.status}


@router.patch("/{document_id}/status")
def update_document_status(document_id: int, status: str, db: Session = Depends(get_db)):
    valid_statuses = {"uploaded", "processing", "indexed", "failed"}
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Status must be one of {valid_statuses}")
    doc = db.query(models.Document).filter_by(id=document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    doc.status = status
    db.commit()
    db.refresh(doc)
    return {"id": doc.id, "status": doc.status}


@router.get("/")
def list_documents(db: Session = Depends(get_db)):
    docs = db.query(models.Document).all()
    return [
        {
            "id": d.id,
            "subject_id": d.subject_id,
            "original_filename": d.original_filename,
            "status": d.status,
            "uploaded_at": d.uploaded_at,
        }
        for d in docs
    ]