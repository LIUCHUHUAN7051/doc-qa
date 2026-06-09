"""
文档问答 RAG 系统
支持多文件上传 (PDF/TXT/Word)，对话记录导出
"""

import os
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# ---------- 文档解析 ----------
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

try:
    import docx
except ImportError:
    docx = None


def extract_text_from_pdf(file) -> str:
    if PdfReader is None:
        st.error("缺少 pypdf 库，请运行: pip install pypdf")
        st.stop()
    reader = PdfReader(file)
    texts = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            texts.append(text)
    return "\n".join(texts)


def extract_text_from_txt(file) -> str:
    return file.read().decode("utf-8", errors="ignore")


def extract_text_from_docx(file) -> str:
    if docx is None:
        st.error("缺少 python-docx 库，请运行: pip install python-docx")
        st.stop()
    doc = docx.Document(file)
    return "\n".join(p.text for p in doc.paragraphs)


# ---------- 文本分块 ----------
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start : start + chunk_size])
        start = start + chunk_size - overlap
    return chunks


# ---------- 检索引擎 (TF-IDF) ----------
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class TfidfRetriever:
    def __init__(self):
        self.chunks: list[str] = []
        self.vectorizer = TfidfVectorizer(
            analyzer="char", ngram_range=(1, 3), max_features=5000
        )
        self._matrix = None

    def add(self, chunks: list[str]):
        self.chunks = chunks
        self._matrix = self.vectorizer.fit_transform(chunks)

    def search(self, query: str, top_k: int = 3) -> list[str]:
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self._matrix)[0]
        top_indices = np.argsort(scores)[::-1][:top_k]
        return [self.chunks[i] for i in top_indices if scores[i] > 0]


# ---------- DeepSeek 客户端 ----------
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY") or st.secrets.get("DEEPSEEK_API_KEY", "")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com/v1",
)

# ========== 页面配置 ==========
st.set_page_config(page_title="文档问答", page_icon="📄", layout="centered")

# ========== 自定义 CSS ==========
st.markdown("""
<style>
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-12px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(20px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulse {
        0%, 100% { box-shadow: 0 0 0 0 rgba(37,99,235,0.15); }
        50%      { box-shadow: 0 0 0 12px rgba(37,99,235,0); }
    }
    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50%      { transform: translateY(-8px); }
    }
    @keyframes shimmer {
        0%   { background-position: -200% center; }
        100% { background-position: 200% center; }
    }
    @keyframes typingDot {
        0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
        40%           { transform: scale(1);   opacity: 1; }
    }
    @keyframes gradientShift {
        0%   { background-position: 0% 50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* 全局 */
    .stApp { background: #f5f7fb; }
    .block-container { padding-top: 2rem !important; animation: fadeIn 0.6s ease-out; }

    /* 头部 */
    .header {
        background: linear-gradient(135deg, #2563eb, #7c3aed, #2563eb);
        background-size: 200% 200%;
        animation: gradientShift 6s ease infinite;
        color: white;
        padding: 1.8rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
    }
    .header h1 { margin: 0; font-size: 1.8rem; font-weight: 700; letter-spacing: 1px; }
    .header p { margin: 0.4rem 0 0; opacity: 0.85; font-size: 0.95rem; }

    /* 侧边栏 */
    section[data-testid="stSidebar"] > div:first-child {
        background: #ffffff;
        border-right: 1px solid #e5e7eb;
    }
    section[data-testid="stSidebar"] .stButton button {
        background: #f3f4f6;
        color: #374151;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        font-size: 0.9rem;
        transition: all 0.2s;
    }
    section[data-testid="stSidebar"] .stButton button:hover {
        background: #e5e7eb;
        border-color: #d1d5db;
        transform: translateY(-1px);
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    section[data-testid="stSidebar"] .stDownloadButton button {
        background: linear-gradient(135deg, #2563eb, #3b82f6);
        color: white;
        border: none;
        border-radius: 10px;
        transition: all 0.25s;
    }
    section[data-testid="stSidebar"] .stDownloadButton button:hover {
        background: linear-gradient(135deg, #1d4ed8, #2563eb);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(37,99,235,0.3);
    }

    /* 文件列表卡片 */
    .file-card {
        background: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        padding: 0.5rem 0.8rem;
        margin: 0.25rem 0;
        font-size: 0.85rem;
        color: #374151;
        animation: slideUp 0.35s ease-out;
        transition: all 0.2s;
    }
    .file-card:hover {
        background: #eff6ff;
        border-color: #93c5fd;
        transform: translateX(3px);
    }
    .file-card::before { content: "📎 "; }

    /* 聊天消息 - 逐条滑入 */
    div[data-testid="stChatMessage"] {
        border-radius: 12px;
        padding: 0.3rem 0;
        animation: slideUp 0.35s ease-out;
    }
    div[data-testid="stChatMessage"] img {
        border-radius: 50%;
    }

    /* 空状态提示 */
    .empty-state {
        text-align: center;
        padding: 4rem 1rem;
        color: #9ca3af;
        animation: fadeIn 0.8s ease-out;
    }
    .empty-state .icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        display: inline-block;
        animation: float 3s ease-in-out infinite;
    }
    .empty-state h3 { color: #6b7280; font-weight: 600; margin-bottom: 0.5rem; }
    .empty-state p { font-size: 0.9rem; }

    /* 输入框 */
    div[data-testid="stChatInput"] input {
        border-radius: 24px !important;
        border: 1px solid #e5e7eb !important;
        padding: 0.6rem 1.2rem !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
        transition: all 0.25s !important;
    }
    div[data-testid="stChatInput"] input:focus {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37,99,235,0.1) !important;
        transform: translateY(-1px);
    }

    /* 上传区域 */
    div[data-testid="stFileUploader"] {
        background: #f9fafb;
        border: 2px dashed #d1d5db;
        border-radius: 12px;
        padding: 1rem;
        transition: all 0.25s;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: #2563eb;
        background: #eff6ff;
        animation: pulse 1.5s ease-in-out infinite;
    }

    /* 分割线 */
    hr { margin: 1rem 0; border-color: #e5e7eb; }

    /* 成功提示 */
    .stAlert { border-radius: 10px; }
    div[data-testid="stSuccess"] { background: #ecfdf5; border: 1px solid #a7f3d0; }
    div[data-testid="stInfo"] { background: #eff6ff; border: 1px solid #bfdbfe; }

    /* 自定义打字动画（spinner 文字） */
    .custom-spinner {
        display: flex; align-items: center; gap: 6px;
        padding: 1rem 0; color: #6b7280;
        font-size: 0.9rem;
    }
    .custom-spinner .dot {
        width: 8px; height: 8px; border-radius: 50%;
        background: #2563eb;
        animation: typingDot 1.4s ease-in-out infinite;
    }
    .custom-spinner .dot:nth-child(2) { animation-delay: 0.2s; }
    .custom-spinner .dot:nth-child(3) { animation-delay: 0.4s; }
</style>
""", unsafe_allow_html=True)

# ========== 全局状态 ==========
if "retriever" not in st.session_state:
    st.session_state.retriever = TfidfRetriever()
if "loaded" not in st.session_state:
    st.session_state.loaded = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "file_list" not in st.session_state:
    st.session_state.file_list = []

# ========== 头部 ==========
st.markdown("""
<div class="header">
    <h1>📄 文档问答</h1>
    <p>上传文档，智能问答 — 支持 PDF · Word · TXT</p>
</div>
""", unsafe_allow_html=True)

# ========== 侧边栏 ==========
with st.sidebar:
    st.markdown("### 📁 上传文档")
    st.caption("支持 PDF / Word / TXT，可多选")

    uploaded_files = st.file_uploader(
        "选择文件",
        type=["pdf", "txt", "docx"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded_files:
        with st.spinner("⏳ 正在处理文档..."):
            all_chunks = []
            names = []
            for f in uploaded_files:
                ext = f.name.rsplit(".", 1)[-1].lower()
                if ext == "pdf":
                    text = extract_text_from_pdf(f)
                elif ext == "docx":
                    text = extract_text_from_docx(f)
                else:
                    text = extract_text_from_txt(f)

                if text.strip():
                    chunks = chunk_text(text)
                    all_chunks.extend(chunks)
                    names.append(f.name)

            if all_chunks:
                st.session_state.retriever = TfidfRetriever()
                st.session_state.retriever.add(all_chunks)
                st.session_state.loaded = True
                st.session_state.file_list = names

    if st.session_state.loaded:
        n = len(st.session_state.file_list)
        st.success(f"✅ 已加载 {n} 个文件")
        for name in st.session_state.file_list:
            st.markdown(f'<div class="file-card">{name}</div>',
                        unsafe_allow_html=True)
        st.divider()

        if st.button("🗑️ 清除文档 & 对话", use_container_width=True):
            st.session_state.retriever = TfidfRetriever()
            st.session_state.loaded = False
            st.session_state.chat_history = []
            st.session_state.file_list = []
            st.rerun()

    if st.session_state.chat_history:
        st.divider()
        chat_text = ""
        for m in st.session_state.chat_history:
            role = "你" if m["role"] == "user" else "AI"
            chat_text += f"### {role}\n{m['content']}\n\n"
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            "💾 导出对话记录",
            data=chat_text,
            file_name=f"对话记录_{now}.md",
            mime="text/markdown",
            use_container_width=True,
        )

# ========== 主界面 ==========
if not st.session_state.loaded:
    st.markdown("""
    <div class="empty-state">
        <div class="icon">📂</div>
        <h3>还没有上传文档</h3>
        <p>在左侧上传 PDF、Word 或 TXT 文件，即可开始提问</p>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("输入你的问题..."):
        st.chat_message("user").markdown(prompt)
        st.session_state.chat_history.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            with st.spinner(""):
                st.markdown("""
                <div class="custom-spinner">
                    <span>🤔 思考中</span>
                    <span class="dot"></span>
                    <span class="dot"></span>
                    <span class="dot"></span>
                </div>
                """, unsafe_allow_html=True)
                relevant_chunks = st.session_state.retriever.search(prompt, top_k=3)
                context = "\n\n---\n\n".join(relevant_chunks)

                system_prompt = (
                    "你是一个基于文档的问答助手。请根据提供的文档内容回答问题。"
                    "如果文档中没有相关信息，请如实说不知道，不要编造。\n\n"
                    f"文档内容：\n{context}"
                )

                try:
                    response = client.chat.completions.create(
                        model="deepseek-chat",
                        messages=[
                            {"role": "system", "content": system_prompt},
                            *[
                                {"role": m["role"], "content": m["content"]}
                                for m in st.session_state.chat_history[-6:]
                            ],
                        ],
                        stream=True,
                    )

                    full_response = ""
                    placeholder = st.empty()
                    for chunk in response:
                        delta = chunk.choices[0].delta.content or ""
                        full_response += delta
                        placeholder.markdown(full_response + "▌")
                    placeholder.markdown(full_response)

                except Exception as e:
                    full_response = f"调用 API 时出错：{e}"
                    st.error(full_response)

                st.session_state.chat_history.append(
                    {"role": "assistant", "content": full_response}
                )
