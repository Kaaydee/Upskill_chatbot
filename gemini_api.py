from fastapi import FastAPI, Request
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.0-flash")
app = FastAPI()

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    messages = data.get("messages", [])

    prompt = messages[-1]["content"] if messages else "Hello"

    try:
        convo = model.start_chat(history=[
            {"role": m["role"], "parts": [m["content"]]}
            for m in messages if m["role"] != "system"
        ])
        response = convo.send_message(prompt)
        return {"reply": response.text}
    except Exception as e:
        return {"reply": f"Lỗi Gemini API: {e}"}
