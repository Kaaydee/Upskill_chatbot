from fastapi import APIRouter, Form
from app.services.chat_service import chat_with_context

router = APIRouter()

@router.post("/")
def chat(user_id: str = Form(...), course_id: str = Form(...), question: str = Form(...)):
    return chat_with_context(user_id, course_id, question)

