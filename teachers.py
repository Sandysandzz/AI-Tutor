# backend/teachers.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.db import get_db
from backend.models import User
from backend.dependencies import require_teacher
from backend.schemas import UserOut

router = APIRouter(prefix="/teachers", tags=["teachers"])


# 1) Get all students of this teacher
@router.get("/me/students", response_model=list[UserOut])
def get_my_students(
    db: Session = Depends(get_db),
    current_teacher: User = Depends(require_teacher)
):
    students = db.query(User).filter(User.teacher_id == current_teacher.id).all()
    return students


# 2) Enroll a student under this teacher
@router.post("/me/enroll/{student_id}")
def enroll_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_teacher: User = Depends(require_teacher)
):
    student = db.query(User).filter(User.id == student_id).first()

    if not student or student.role != "student":
        raise HTTPException(status_code=404, detail="Student not found")

    student.teacher_id = current_teacher.id
    db.commit()
    db.refresh(student)

    return {"status": "enrolled", "student_id": student.id}
