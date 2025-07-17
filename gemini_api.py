from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
from google.generativeai import configure, GenerativeModel
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO
import base64

# Load API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Cấu hình Gemini
configure(api_key=api_key)
client = genai.Client(api_key=api_key)

# Tạo ảnh từ prompt, trả về mô tả và base64 ảnh
def generate_image_from_prompt(prompt):
    try:
        prompt = "Hãy mô tả và tạo ảnh bằng tiếng Việt.\n" + prompt
        response = client.models.generate_content(
            model="gemini-2.0-flash-preview-image-generation",
            contents=prompt,
            config=types.GenerateContentConfig(response_modalities=['TEXT', 'IMAGE'])
        )

        text_description = ""
        image_base64 = None

        for part in response.candidates[0].content.parts:
            if part.text is not None:
                text_description = part.text
            elif part.inline_data is not None:
                image = Image.open(BytesIO(part.inline_data.data))
                buffered = BytesIO()
                image.save(buffered, format="PNG")
                image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return text_description, image_base64

    except Exception as e:
        return f"Lỗi khi tạo ảnh: {e}", None

# Function declarations
function_declarations = [
    {
        "name": "generate_image",
        "description": "Tạo một hình ảnh từ mô tả văn bản",
        "parameters": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Mô tả hình ảnh cần tạo"}
            },
            "required": ["prompt"]
        }
    }
]

model = GenerativeModel(
    model_name="gemini-2.0-flash",
    tools=[{"function_declarations": function_declarations}]
)

# FastAPI app
app = FastAPI()

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    messages = data.get("messages", [])
    prompt = messages[-1]["content"] if messages else "Hello"

    try:
        response = model.generate_content(prompt)
        parts = response.candidates[0].content.parts

        if parts and hasattr(parts[0], 'function_call'):
            call = parts[0].function_call
            if call:
                func_name = call.name
                args = call.args or {}

                if func_name == "generate_image":
                    prompt_text = args.get("prompt")
                    if prompt_text:
                        text, image_b64 = generate_image_from_prompt(prompt_text)
                        return JSONResponse(content={
                            "reply": text,
                            "image_base64": f"data:image/png;base64,{image_b64}" if image_b64 else None
                        })
                    else:
                        return JSONResponse(content={"reply": "Thiếu mô tả ảnh."})
                else:
                    return JSONResponse(content={"reply": "Hàm không được hỗ trợ."})
            else:
                return JSONResponse(content={
                    "reply": parts[0].text if hasattr(parts[0], 'text') else "Không có nội dung."
                })
        else:
            return JSONResponse(content={
                "reply": parts[0].text if parts and hasattr(parts[0], 'text') else "Không có nội dung."
            })

    except Exception as e:
        return JSONResponse(content={"reply": f"[Lỗi backend]: {e}"})
