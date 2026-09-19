from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# ---------- Institution ----------
class InstitutionCreate(BaseModel):
    name: str

class InstitutionOut(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Class ----------
class ClassCreate(BaseModel):
    institution_id: int
    name: str

class ClassOut(BaseModel):
    id: int
    institution_id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Subject ----------
class SubjectCreate(BaseModel):
    class_id: int
    name: str

class SubjectOut(BaseModel):
    id: int
    class_id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Classroom Session ----------
class SessionCreate(BaseModel):
    class_id: int
    teacher_id: int

class SessionOut(BaseModel):
    id: int
    class_id: int
    teacher_id: int
    status: str
    started_at: datetime
    ended_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        # ---------- Questions & Answers ----------
class QuestionIn(BaseModel):
    session_id: int
    student_id: int
    subject_id: int
    text: str
    language: str = "en"

class SourceItem(BaseModel):
    chapter: str
    page: int

class AnswerOut(BaseModel):
    question_id: int
    answer: str
    language: str
    style: str
    verified: bool
    verification_status: str
    sources: list[SourceItem]
    cached: bool
    # ---------- Teacher Approval ----------
class CorrectionIn(BaseModel):
    corrected_text: str

class ApprovalOut(BaseModel):
    id: int
    question_id: int
    answer_id: int
    status: str
    # ---------- Auth ----------
class TeacherSignup(BaseModel):
    username: str
    password: str
    full_name: str
    institution_id: int

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    teacher_id: int
    username: str
    full_name: str
    message: str = "Login successful"