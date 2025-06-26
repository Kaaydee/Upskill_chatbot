from fastapi import APIRouter
from app.services.analysis_service import analyze_student_results

router = APIRouter()

@router.post("/analyze")
def analyze():
    return analyze_student_results()