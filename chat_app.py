import hashlib
import streamlit as st
import requests
import fitz
from docx import Document
from io import BytesIO
import base64
from datetime import datetime
from pydub import AudioSegment
from streamlit_mic_recorder import mic_recorder
import uuid
from weasyprint import HTML
from io import BytesIO
import html
from gtts import gTTS
import tempfile


# Hàm chuyển đổi văn bản thành giọng nói và tạo file âm thanh
def text_to_speech(text, lang="vi"):
    tts = gTTS(text=text, lang=lang, slow=False)
    # Lưu file tạm thời
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmpfile:
        tts.save(tmpfile.name)
        return tmpfile.name


# Hàm tạo PDF từ câu hỏi và câu trả lời
def create_pdf_html(question, answer):
    question_escaped = html.escape(question)
    answer_escaped = html.escape(answer)

    html_content = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: 'DejaVu Sans', monospace, monospace; }}
            h2 {{ color: #2e6c80; }}
            pre {{
                background: #f4f4f4; 
                padding: 10px; 
                border-radius: 5px; 
                white-space: pre-wrap;
                font-family: monospace;
                font-size: 12pt;
            }}
        </style>
    </head>
    <body>
        <h2>User:</h2>
        <pre>{question_escaped}</pre>
        <h2>UpSkill's Assistant:</h2>
        <pre>{answer_escaped}</pre>
    </body>
    </html>
    """

    pdf_io = BytesIO()
    HTML(string=html_content).write_pdf(pdf_io)
    pdf_io.seek(0)
    return pdf_io


# Hàm render footer
def render_footer():
    st.markdown("""
    <style>
    .fixed-footer {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        width: 100% !important;
        background-color: white;
        padding: 10px 0;
        text-align: center;
        font-size: 14px;
        color: gray;
        border-top: 1px solid #eee;
        z-index: 9999;
        box-shadow: 0 -2px 5px rgba(0,0,0,0.1);
        pointer-events: auto;
    }
    </style>

    <div class='fixed-footer'>
        📞 Hotline: <strong>093 448 94 05</strong><br>
        ✉️ Email: <a href="mailto:upskill@upskill.edu.vn">upskill@upskill.edu.vn</a>
    </div>
    """, unsafe_allow_html=True)


# --- Giao diện ---
st.set_page_config(page_title="UpskillChat", layout="centered")
st.image("logo.jpg")


def get_image_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# Lấy base64 của logo để dùng làm avatar
logo_base64 = get_image_base64("logo.jpg")
avatar_logo = f"data:image/png;base64,{logo_base64}"
logo_base641 = get_image_base64("logo.png")
avatar_logo1 = f"data:image/png;base64,{logo_base641}"
st.title("💬 UpskillChat")


# --- Hàm đọc file ---
def read_txt(file): return file.read().decode("utf-8")


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

if "uploaded_once" not in st.session_state:
    st.session_state.uploaded_once = False

# --- Sidebar ---
st.sidebar.markdown(
    f"""
    <div style="text-align: center; margin-bottom: 20px;">
        <img src="{avatar_logo}" style="height: 60px;" />
    </div>
    """,
    unsafe_allow_html=True
)
st.sidebar.subheader("📄 Quản lý tài liệu")

if st.session_state.uploaded_once:
    if st.sidebar.button("🗑️ Xoá tài liệu đã tải"):
        st.session_state.messages = [
            msg for msg in st.session_state.messages
            if not msg.get("content", "").startswith("Nội dung tài liệu:")
        ]
        st.session_state.uploaded_once = False
        st.sidebar.success("✅ Đã xoá nội dung tài liệu.")

uploaded_file = st.sidebar.file_uploader(
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
        st.session_state.messages.append({
            "role": "user",
            "content": f"Nội dung tài liệu:\n{file_text}"
        })
        st.session_state.uploaded_once = True
        st.sidebar.success(f"✅ Đã thêm nội dung từ: {uploaded_file.name}")

# --- Hiển thị lịch sử chat ---
for i, msg in enumerate(st.session_state.messages):
    if msg["role"] == "system" or msg["content"].startswith("Nội dung tài liệu:"):
        continue

    # Lọc bỏ các ký tự đặc biệt
    cleaned_content = msg["content"].replace("*", "").strip()

    # Sử dụng logo làm avatar cho assistant
    avatar = None if msg["role"] == "user" else avatar_logo1

    with st.chat_message(msg["role"], avatar=avatar):
        # Thay đổi cách hiển thị tin nhắn
        if msg["role"] == "user":
            st.markdown(f"**User:** {cleaned_content}")  # In đậm chữ User
        else:
            st.markdown(cleaned_content)  # Tin nhắn AI không có định dạng đặc biệt

        # Chỉ thêm nút Save cho tin nhắn assistant không có hình ảnh
        if msg["role"] == "assistant" and not msg.get("image_base64"):
            if i > 0 and st.session_state.messages[i - 1]["role"] == "user":
                question = st.session_state.messages[i - 1]["content"].replace("*", "").strip()
                answer = cleaned_content
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"upskill_chat_{timestamp}.txt"
                content = f"User: {question}\n\n{answer}"  # Định dạng lưu file

                pdf_buffer = create_pdf_html(question, answer)
                st.download_button(
                    label="💾 Tải Q&A",
                    data=pdf_buffer,
                    file_name=f"upskill_chat_{timestamp}.pdf",
                    mime="application/pdf",
                    key=f"save_pdf_{i}"
                )

                # Tạo TTS cho câu trả lời
                audio_file = text_to_speech(answer, lang="vi")  # Chuyển đổi văn bản thành giọng nói tiếng Việt
                with open(audio_file, "rb") as audio_data:
                    st.download_button(
                        label="🔊 Tải âm thanh trả lời",
                        data=audio_data,
                        file_name=f"answer_{timestamp}.mp3",
                        mime="audio/mp3"
                    )

        # Xử lý hiển thị hình ảnh nếu có
        if msg["role"] == "assistant" and msg.get("image_base64"):
            st.image(msg["image_base64"], caption="🖼️ Hình ảnh được tạo", use_container_width=True)
            image_bytes = base64.b64decode(msg["image_base64"].split(",")[-1])
            image_key = hashlib.md5(image_bytes).hexdigest()

            st.download_button(
                label="⬇️ Tải ảnh",
                data=image_bytes,
                file_name="image.png",
                mime="image/png",
                key=f"download_{image_key}"
            )

# Khởi tạo biến key nếu chưa có
if "recorder_key" not in st.session_state:
    st.session_state.recorder_key = 0

# Tạo recorder với key động (mỗi lần khác nhau)
voice_input = mic_recorder(
    start_prompt="🎙️ Nhấn để ghi",
    stop_prompt="🛑 Dừng",
    key=f"recorder_{st.session_state.recorder_key}",
    just_once=False
)

# Xử lý khi có dữ liệu
if voice_input:
    try:
        if isinstance(voice_input, dict) and "bytes" in voice_input:
            audio_bytes = voice_input["bytes"]
        elif isinstance(voice_input, bytes):
            audio_bytes = voice_input
        else:
            st.error("voice_input không hợp lệ!")
            st.stop()

        # Convert webm to mp3
        audio_segment = AudioSegment.from_file(BytesIO(audio_bytes), format="webm")
        mp3_io = BytesIO()
        audio_segment.export(mp3_io, format="mp3")
        mp3_io.seek(0)

        # Gửi lên voice2text
        response = requests.post(
            "http://31.97.220.12:8080/voice2text",
            files={"audio": ("voice.mp3", mp3_io, "audio/mpeg")}
        )
        response.raise_for_status()
        text = response.json().get("text", "").strip()

        if not text:
            st.warning("⚠️ Không nhận diện được nội dung giọng nói.")
        else:
            st.session_state.messages.append({"role": "user", "content": text})
            with st.chat_message("user"):
                st.markdown(f"**User (từ giọng nói):** {text}")

            # Gửi tới Chat API
            with st.spinner("💭 Đang suy nghĩ..."):
                res = requests.post(
                    "http://localhost:8000/chat",
                    json={"messages": st.session_state.messages}
                )
                res_data = res.json()
                reply = res_data.get("reply", "[Lỗi: Không có phản hồi từ server]")
                image_base64 = res_data.get("image_base64")

            st.session_state.messages.append({
                "role": "assistant",
                "content": reply,
                "image_base64": image_base64
            })

        # Tăng key recorder để có thể ghi tiếp lần sau
        st.session_state.recorder_key += 1
        render_footer()
        st.rerun()

    except Exception as e:
        st.error(f"Lỗi xử lý voice: {e}")

# --- Xử lý chat thủ công ---
if prompt := st.chat_input("Gõ câu hỏi của bạn tại đây..."):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(f"**User:** {prompt}")

    try:
        render_footer()
        with st.spinner("💭 Đang suy nghĩ..."):
            res = requests.post(
                "http://localhost:8000/chat",
                json={"messages": st.session_state.messages}
            )
            res_data = res.json()
            reply = res_data.get("reply", "[Lỗi: Không có phản hồi từ server]")
            image_base64 = res_data.get("image_base64")

    except Exception as e:
        reply = f"[Lỗi khi gửi tới API]: {e}"
        image_base64 = None

    st.session_state.messages.append({
        "role": "assistant",
        "content": reply,
        "image_base64": image_base64
    })
    render_footer()
    st.rerun()

# --- Hiển thị footer luôn ở cuối trang ---
render_footer()
