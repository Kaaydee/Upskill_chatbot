# 🤖 Upskill Chatbot

Upskill Chatbot là một ứng dụng hỗ trợ người học tương tác với tài liệu học tập thông qua trợ lý AI sử dụng mô hình Gemini của Google. Người dùng có thể upload tài liệu (.pdf, .docx, .txt) và đặt câu hỏi trực tiếp dựa trên nội dung đó.

---

## 🚀 Chức năng chính

- Chat với AI về chủ đề học tập
- Hỗ trợ upload tài liệu (PDF, Word, TXT)
- Xử lý nội dung từ tài liệu và đưa vào hội thoại
- Trả lời ngắn gọn, chính xác (~150 tokens)
- Giao diện thân thiện với người dùng thông qua Streamlit

---

## 🧩 Cài đặt môi trường

### 1. Tạo môi trường ảo (tuỳ chọn)

```bash
python -m venv venv
source venv/bin/activate        # Trên Mac/Linux
venv\Scripts\activate           # Trên Windows

2. Cài đặt thư viện
pip install -r requirements.txt
🔑 Lấy API Key Gemini
Truy cập: https://aistudio.google.com/app/apikey

Nhấn "Create API Key"

Sao chép API key được tạo

🔐 Tạo file .env
Tạo file .env trong thư mục dự án và thêm dòng sau:


GOOGLE_API_KEY=your_gemini_api_key_here
Thay your_gemini_api_key_here bằng API key vừa tạo ở bước trên.

▶️ Chạy ứng dụng
1. Khởi chạy FastAPI backend
uvicorn gemini_api:app --reload

2. Khởi chạy giao diện người dùng với Streamlit
streamlit run chat.py



📌 Lưu ý
Mỗi lần chỉ xử lý 1 tài liệu

Tài liệu mới sẽ thay thế nội dung cũ

Hỗ trợ file < 10MB (PDF, DOCX, TXT)

Đảm bảo backend (uvicorn) đang chạy trước khi sử dụng giao diện chat

📧 Liên hệ
Website: https://upskill.edu.vn/