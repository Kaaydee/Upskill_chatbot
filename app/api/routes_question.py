from fastapi import APIRouter
from app.services.question_service import generate_questions_with_gemini

router = APIRouter()

@router.post("/generate")
def generate():
    return generate_questions_with_gemini()