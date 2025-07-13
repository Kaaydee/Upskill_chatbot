import json
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv()

def generate_questions_with_gemini():
    with open("app/data/extended_questions.json", "r", encoding="utf-8") as f:
        extended_questions = json.load(f)

    def build_prompt(questions):
        prompt = "Dựa trên các câu hỏi dưới đây, hãy tạo thêm 3 câu hỏi tương tự.\n"
        for i, q in enumerate(questions, 1):
            prompt += f"Câu {i}: {q['question']}\n"
            for opt_key, opt_val in q["options"].items():
                prompt += f"  {opt_key}. {opt_val}\n"
            prompt += f"Đáp án: {q['answer']}\nChủ đề: {q['topic']}\n\n"
        prompt += "\n👉 Trả lời bằng JSON."
        return prompt

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))
    prompt = build_prompt(extended_questions)
    response = llm.invoke([HumanMessage(content=prompt)])
    return {"result": response.content}