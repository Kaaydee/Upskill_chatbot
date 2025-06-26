import json
import random
from typing import List
from app.models.schema import QuestionItem, StudentAnswer
from app.services.llm_question_generator import generate_questions_llm


def analyze_errors(exam_data: List[QuestionItem], student_answers: List[StudentAnswer]) -> List:
    question_map = {q.question_id: q for q in exam_data}
    topic_errors = {}

    for ans in student_answers:
        qid = ans.question_id
        selected = ans.selected_option
        correct = question_map[qid].answer
        topic = question_map[qid].topic
        if selected != correct:
            topic_errors[topic] = topic_errors.get(topic, 0) + 1

    top_wrong = sorted(topic_errors.items(), key=lambda x: -x[1])[:3]
    return top_wrong

def filter_questions_by_topics(exam_data: List[QuestionItem], topics):
    topic_set = set(t[0] for t in topics)
    return [q for q in exam_data if q.topic in topic_set]

def analyze_and_generate_questions_from_file(course_id: str, user_id: str):
    with open(f"app/data/exams/{course_id}.json", encoding="utf-8") as f:
        exam_data = [QuestionItem(**q) for q in json.load(f)]

    with open(f"app/data/answers/{user_id}-{course_id}.json", encoding="utf-8") as f:
        student_answers = [StudentAnswer(**s) for s in json.load(f)]

    top_wrong_topics = analyze_errors(exam_data, student_answers)
    base_questions = filter_questions_by_topics(exam_data, top_wrong_topics)
    new_questions = generate_questions_llm(base_questions)

    return {
        "top_wrong_topics": top_wrong_topics,
        "new_questions": new_questions
    }
