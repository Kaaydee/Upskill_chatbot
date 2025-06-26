from fastapi import APIRouter, Form
from app.services.learning_feedback_service import analyze_and_generate_questions_from_file
from app.models.schema import FeedbackResponse

router = APIRouter()

@router.post("/", response_model=FeedbackResponse)
def feedback(user_id: str = Form(...), course_id: str = Form(...)):
    return analyze_and_generate_questions_from_file(
        course_id=course_id,
        user_id=user_id
    )