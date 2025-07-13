import streamlit as st
import requests
import fitz 
from docx import Document

# --- Giao diện ---
st.set_page_config(page_title="UpskillChat", layout="centered")
st.image("logo.jpg")
st.title("💬 UpskillChat Demo")

# --- Hàm đọc file ---
def read_txt(file):
    return file.read().decode("utf-8")

def read_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    return "\n".join(page.get_text() for page in doc)

def read_docx(file):
    doc = Document(file)
    return "\n".join(para.text for para in doc.paragraphs)

# --- Khởi tạo session ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": (
                "Bạn ưu tiên sử dụng ngôn ngữ theo ngôn ngữ được prompt cung cấp. "
                "Nếu không có ngôn ngữ nào được cung cấp, hãy sử dụng tiếng Việt. "
                "Bạn là một trợ lý AI chuyên hỗ trợ giải đáp các câu hỏi liên quan đến hệ thống học tập. "
                "Bạn có thể nhận câu hỏi trực tiếp từ người dùng hoặc dựa vào nội dung được cung cấp từ các tệp tài liệu. "
                "Luôn trả lời ngắn gọn, rõ ràng, và chính xác trong phạm vi khoảng 150 tokens. "
                "Nếu không đủ thông tin, hãy đề xuất người dùng cung cấp thêm chi tiết hoặc tải lên tài liệu liên quan."
            )
        }
    ]

# --- Đảm bảo file chỉ được thêm 1 lần ---
if "uploaded_once" not in st.session_state:
    st.session_state.uploaded_once = False

# --- Upload file nằm trong dấu cộng (sidebar) ---
# --- Upload file nằm trong dấu cộng (sidebar) ---
with st.sidebar:
    st.subheader("📄 Quản lý tài liệu")

    # Nút xóa nội dung tài liệu đã upload
    if st.session_state.uploaded_once:
        if st.button("🗑️ Xoá tài liệu đã tải"):
            # Xóa nội dung tài liệu khỏi messages
            st.session_state.messages = [
                msg for msg in st.session_state.messages
                if not msg.get("content", "").startswith("Nội dung tài liệu:")
            ]
            st.session_state.uploaded_once = False
            st.success("✅ Đã xoá nội dung tài liệu. Bạn có thể tải tài liệu khác.")

    # Upload tài liệu mới
    uploaded_file = st.file_uploader(
        "📎 Tải tài liệu (.pdf, .docx, .txt)",
        type=["pdf", "docx", "txt"]
    )

    if uploaded_file and not st.session_state.uploaded_once:
        file_text = ""
        if uploaded_file.type == "application/pdf":
            file_text = read_pdf(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            file_text = read_docx(uploaded_file)
        elif uploaded_file.type == "text/plain":
            file_text = read_txt(uploaded_file)

        if file_text:
            # Thêm nội dung file vào messages
            st.session_state.messages.append({
                "role": "user",
                "content": f"Nội dung tài liệu:\n{file_text}"
            })
            st.session_state.uploaded_once = True
            st.success(f"✅ Đã thêm nội dung từ: {uploaded_file.name}")


# --- Hiển thị lịch sử chat (không hiển thị message system) ---
for msg in st.session_state.messages:
    if msg["role"] == "system" or msg["content"].startswith("Nội dung tài liệu:"):
        continue
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.markdown(f"**{'Upskill:' if msg['role'] == 'user' else ''}** {msg['content']}")

# --- Nhập prompt từ người dùng ---
if prompt := st.chat_input("Gõ câu hỏi của bạn tại đây..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(f"**Upskill:** {prompt}")

    # Gửi tới backend FastAPI
    try:
        with st.spinner("💭 Đang suy nghĩ..."):
            res = requests.post(
                "http://localhost:8000/chat",
                json={"messages": st.session_state.messages}
            )
            reply = res.json().get("reply", "[Lỗi: Không có phản hồi từ server]")
    except Exception as e:
        reply = f"[Lỗi khi gửi tới API]: {e}"

    # Hiển thị phản hồi
    st.session_state.messages.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant", avatar="logo.png"):
        st.markdown(reply)
