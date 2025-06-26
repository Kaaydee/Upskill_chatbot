from fastapi import FastAPI
from app.api import routes_chat, routes_question, routes_detection, routes_index, routes_feedback

app = FastAPI()
app.include_router(routes_chat.router, prefix="/chat", tags=["Chatbot"])
# app.include_router(routes_question.router, prefix="/question", tags=["Question"])
# app.include_router(routes_detection.router, prefix="/detection", tags=["Detection"])
app.include_router(routes_index.router, prefix="/upload", tags=["upload"])
app.include_router(routes_feedback.router, prefix="/learning", tags=["Learning"])
