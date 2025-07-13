from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import InMemoryChatMessageHistory
from fpdf import FPDF

# Load biến môi trường
load_dotenv()
store = {}

# Kết nối Mongo
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["upskill_db"]
chat_collection = db["chat_history"]

def get_session_history(session_id):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

def generate_questions_from_material(user_id, course_id, question, topic=None):
    namespace = f"{user_id}-{course_id}"
    history = get_session_history(namespace)

    # Pinecone setup
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index("upskill")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    vectorstore = PineconeVectorStore(index=index, embedding=embeddings, namespace=namespace)

    docs = vectorstore.similarity_search(topic or question, k=20)

    print("📄 Tài liệu liên quan:")
    for i, doc in enumerate(docs, 1):
        print(f"\n--- Tài liệu {i} ---")
        print("🔹 Metadata:", doc.metadata)
        print("🔸 Nội dung:", doc.page_content[:300], "...")

    context = "\n\n".join([d.page_content for d in docs]) if docs else "Không có nội dung."

    template = """
Bạn là một trợ lý học tập. Dựa vào tài liệu sau, hãy tạo ra một danh sách các câu hỏi luyện tập cho người học, tập trung vào nội dung chính, có thể kiểm tra mức độ hiểu của học viên.

Lưu ý:
- Câu hỏi nên ngắn gọn, rõ ràng.
- Nếu phù hợp, có thể bao gồm cả câu hỏi trắc nghiệm và tự luận.

TÀI LIỆU:
{context}

LỊCH SỬ TƯƠNG TÁC TRƯỚC (nếu có):
{history}
"""

    prompt = ChatPromptTemplate.from_messages([
        ("system", template),
        ("human", "{user_question}")
    ])

    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=os.getenv("GOOGLE_API_KEY"))

    chain = (
        {
            "context": lambda _: context,
            "history": lambda _: "\n".join([m.content for m in history.messages]),
            "user_question": lambda _: question
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    result = chain.invoke({})

    # Check đã có document chưa
    existing_doc = chat_collection.find_one({
        "user_id": user_id,
        "course_id": course_id
    })

    if existing_doc:
        # Tính id mới
        next_id = len(existing_doc.get("history", [])) + 1
        chat_collection.update_one(
            {"_id": existing_doc["_id"]},
            {
                "$push": {
                    "history": {
                        "id": next_id,
                        "question": question,
                        "answer": result
                    }
                },
                "$set": {"timestamp": datetime.utcnow()}
            }
        )
    else:

        chat_collection.insert_one({
            "user_id": user_id,
            "course_id": course_id,
            "history": [
                {
                    "id": 1,
                    "question": question,
                    "answer": result
                }
            ],
            "timestamp": datetime.utcnow()
        })

    return {"questions": result}


def export_history_to_txt(user_id: str, course_id: str, output_path: str = "chat_history.txt"):
    record = chat_collection.find_one({
        "user_id": user_id,
        "course_id": course_id
    })

    if not record or "history" not in record:
        print("❌ Không có lịch sử nào để xuất.")
        return

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(f"LỊCH SỬ HỌC TẬP - {user_id.upper()} ({course_id.upper()})\n\n")

        for entry in record["history"]:
            f.write(f"Câu hỏi {entry['id']}:\n")
            f.write(f"CÂU HỎI: {entry['question']}\n")
            f.write(f"TRẢ LỜI: {entry['answer']}\n")
            if "timestamp" in entry:
                f.write(f"Thời gian: {entry['timestamp']}\n")
            f.write("\n" + "-"*40 + "\n\n")

    print(f"✅ Đã xuất TXT: {output_path}")


def main():
    result = generate_questions_from_material(
        user_id="kiet1",
        course_id="Transactions",
            question="Tạo bộ câu hỏi 10 câu trắc nghiệm Lesson 1: Overview of Transactions and Locks về Transactions và Locked trong Microsoft SQL Server.",
            topic="Transactions"
    )

    print("\n========== CÂU HỎI SINH RA ==========")
    print(result["questions"])

if __name__ == "__main__":
    main()
    export_history_to_txt(user_id="kiet1", course_id="Transactions", output_path="transactions_chat_history.txt")
