import json
import re
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from app.models.schema import GeneratedQuestion

load_dotenv()


def extract_json_content(text: str) -> str:
    pattern = r"```(?:json\s*)?(.*?)```"
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    return match.group(1).strip() if match else text.strip()


def transform_options(options_list: list) -> dict:
    options_dict = {}
    for i, opt in enumerate(options_list):
        key = chr(65 + i)
        options_dict[key] = opt
    return options_dict


def generate_questions_llm(base_questions):
    def build_prompt(questions):
        prompt = "Dựa trên các câu hỏi dưới đây, hãy tạo thêm 3 câu hỏi tương tự.\n"
        for i, q in enumerate(questions, 1):
            prompt += f"Câu {i}: {q.question}\n"
            for opt_key, opt_val in q.options.items():
                prompt += f"  {opt_key}. {opt_val}\n"
            prompt += f"Đáp án: {q.answer}\nChủ đề: {q.topic}\n\n"

        prompt += """
 TRẢ LỜI THEO ĐÚNG ĐỊNH DẠNG JSON SAU:
[
  {
    "question": "...",
    "options": {"A": "...", "B": "...", "C": "...", "D": "..."},
    "answer": "A|B|C|D",
    "topic": "..."
  },
  ...
]
"""
        return prompt

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))
    prompt = build_prompt(base_questions)
    response = llm.invoke([HumanMessage(content=prompt)])

    raw = response.content.strip()
    # print(repr(raw))

    clean = extract_json_content(raw)
    # print(repr(clean))

    try:
        parsed = json.loads(clean)
        questions = []
        for item in parsed:
            if isinstance(item["options"], list):
                item["options"] = transform_options(item["options"])

            questions.append(GeneratedQuestion(
                question=item["question"],
                options=item["options"],
                answer=item["answer"],
                topic=item["topic"]
            ))
        return questions
    except Exception as e:
        print("error:", e)
        print("clean", clean)
        raise ValueError("Gemini returned invalid JSON format")