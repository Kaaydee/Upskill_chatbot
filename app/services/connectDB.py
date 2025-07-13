from fpdf import FPDF
from pymongo import MongoClient
import os
# Kết nối Mongo
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client["upskill_db"]
chat_collection = db["chat_history"]
def export_history_to_pdf(user_id: str, course_id: str, output_path: str = "chat_history.pdf"):
    record = chat_collection.find_one({
        "user_id": user_id,
        "course_id": course_id
    })

    if not record or "history" not in record:
        print("❌ Không có lịch sử nào để xuất.")
        return

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_title(f"Lịch sử học tập - {user_id} ({course_id})")

    pdf.cell(200, 10, txt=f"Lịch sử học tập - {user_id} ({course_id})", ln=True, align="C")

    for entry in record["history"]:
        pdf.set_font("Arial", style="B", size=11)
        pdf.cell(0, 10, f"\nCâu hỏi {entry['id']}:", ln=True)
        pdf.set_font("Arial", size=11)
        pdf.multi_cell(0, 10, f"👉 {entry['question']}")
        pdf.set_font("Arial", style="I", size=11)
        pdf.multi_cell(0, 10, f"📘 Trả lời:\n{entry['answer']}")
        pdf.ln(5)

    pdf.output(output_path)
    print(f"✅ Đã xuất PDF: {output_path}")
if __name__ == "__main__":
    export_history_to_pdf(user_id="u1", course_id="gan", output_path="gan_chat_history.pdf")
