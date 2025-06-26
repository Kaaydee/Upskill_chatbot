from pydantic import BaseModel
from typing import List, Dict, Union

class QuestionItem(BaseModel):
    question_id: int
    question: str
    options: Dict[str, str]
    answer: str
    topic: str

class StudentAnswer(BaseModel):
    question_id: int
    selected_option: str

class GeneratedQuestion(BaseModel):
    question: str
    options: Union[Dict[str, str], List[str]]
    answer: str
    topic: str

class FeedbackResponse(BaseModel):
    top_wrong_topics: List[List]
    new_questions: List[GeneratedQuestion]
