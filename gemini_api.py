from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import google.generativeai as genai
from dotenv import load_dotenv
import os
from PIL import Image
from io import BytesIO
import base64

# Load .env
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Model cho chat và model tạo ảnh
chat_model = genai.GenerativeModel("gemini-2.0-flash")
image_model = genai.GenerativeModel("gemini-2.0-flash-preview-image-generation")


# Hàm phân loại: prompt có phải là yêu cầu tạo ảnh không?
def should_generate_image(prompt: str) -> bool:
    try:
        classification_prompt = f"""
Bạn là một AI phân loại. Câu sau đây có phải là yêu cầu tạo ảnh không?

Câu: "{prompt}"

Trả lời duy nhất bằng: "YES" nếu là yêu cầu tạo ảnh, hoặc "NO" nếu không phải.
"""
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(classification_prompt, stream=False)
        answer = response.text.strip().lower()
        return "yes" in answer
    except Exception as e:
        print(f"Lỗi phân loại ảnh: {e}")
        return False


# Tạo ảnh từ prompt, trả về mô tả + base64
def generate_image_from_prompt(prompt: str):
    try:
        full_prompt = "Hãy mô tả và tạo ảnh bằng tiếng Việt.\n" + prompt
        response = image_model.generate_content(
            contents=full_prompt,
            generation_config={"response_modalities": ["TEXT", "IMAGE"]},
            stream=False
        )

        text_description = ""
        image_base64 = None

        for part in response.candidates[0].content.parts:
            if hasattr(part, "text") and part.text:
                text_description = part.text
            elif hasattr(part, "inline_data") and part.inline_data:
                image = Image.open(BytesIO(part.inline_data.data))
                buffered = BytesIO()
                image.save(buffered, format="PNG")
                image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return text_description, image_base64

    except Exception as e:
        return f"Lỗi khi tạo ảnh: {e}", None


# Tạo FastAPI app
app = FastAPI()

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    messages = data.get("messages", [])
    prompt = messages[-1]["content"] if messages else "Hello"

    # Phân loại xem có cần tạo ảnh không
    if should_generate_image(prompt):
        try:
            text, image_b64 = generate_image_from_prompt(prompt)
            return JSONResponse(content={
                "reply": text,
                "image_base64": f"data:image/png;base64,{image_b64}" if image_b64 else None
            })
        except Exception as e:
            return JSONResponse(content={"reply": f"Lỗi khi tạo ảnh: {e}"})

    # Trường hợp xử lý chat bình thường
    try:
        convo = chat_model.start_chat(history=[
            {"role": m["role"], "parts": [m["content"]]}
            for m in messages if m["role"] != "system"
        ])
        response = convo.send_message(prompt)
        return {"reply": response.text}
    except Exception as e:
        return {"reply": f"Lỗi Gemini API: {e}"}

