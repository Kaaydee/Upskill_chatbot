import json
import random
import copy

def analyze_student_results():
    with open("app/data/questions_data_with_id.json", "r", encoding="utf-8") as f:
        questions = json.load(f)
    with open("app/data/student_answers_sample.json", "r", encoding="utf-8") as f:
        student_results = json.load(f)

    question_map = {q["question_id"]: q for q in questions}
    topic_errors = {}

    for student in student_results:
        for ans in student["answers"]:
            qid = ans["question_id"]
            selected = ans["selected_option"]
            correct = question_map[qid]["answer"]
            topic = question_map[qid]["topic"]
            if selected != correct:
                topic_errors[topic] = topic_errors.get(topic, 0) + 1

    top_wrong_topics = sorted(topic_errors.items(), key=lambda x: -x[1])[:3]
    new_questions = []
    next_id = max(q["question_id"] for q in questions) + 1

    for topic, _ in top_wrong_topics:
        base_questions = [q for q in questions if q["topic"] == topic]
        for _ in range(2):
            template = random.choice(base_questions)
            new_q = copy.deepcopy(template)
            new_q["question_id"] = next_id
            new_q["question"] += " (mở rộng)"
            new_q["options"] = dict(random.sample(new_q["options"].items(), len(new_q["options"])))
            next_id += 1
            new_questions.append(new_q)

    with open("app/data/extended_questions.json", "w", encoding="utf-8") as f:
        json.dump(new_questions, f, indent=2, ensure_ascii=False)

    return {"topics": top_wrong_topics, "new_questions": len(new_questions)}

