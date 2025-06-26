from fastapi import APIRouter, UploadFile, File, Form
from app.services.index_service import index_user_course_pdf

router = APIRouter()

@router.post("/")
def index(user_id: str = Form(...), course_id: str = Form(...), file: UploadFile = File(...)):
    return index_user_course_pdf(user_id, course_id, file)
