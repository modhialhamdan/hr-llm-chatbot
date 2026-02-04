import sys
from pathlib import Path

# Add project root to PYTHONPATH for Streamlit
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import streamlit as st
from src.chat.memory import ChatMemory
from src.chat.router import answer_question
from src.chat.exporter import export_txt, export_pdf

st.set_page_config(page_title="HR Analytics Chatbot", page_icon="💬", layout="centered")
st.markdown(
        """
    <style>
    /* ===============================
    GLOBAL BACKGROUND (near-black)
    =============================== */
    html, body, .stApp {
        background-color: #07070B !important;
        color: #E6E6F0 !important;
    }

    /* Main container */
    .main .block-container {
        background-color: transparent !important;
        padding: 2.5rem 2rem 6rem 2rem;
    }

    /* ===============================
    HEADER
    =============================== */
    h1 {
        font-weight: 700 !important;
        font-size: 2.4rem !important;
        background: linear-gradient(135deg, #C77DFF, #C74968);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .stCaption {
        color: #A9A9BD !important;
    }

    /* ===============================
    CHAT MESSAGES
    =============================== */
    .stChatMessage {
        background-color: #0E0E16 !important;
        border: 1px solid rgba(199,125,255,0.15) !important;
        border-radius: 14px !important;
        padding: 1.2rem !important;
    }

    /* User */
    .stChatMessage[data-testid*="user"] {
        border-left: 4px solid #C77DFF !important;
    }

    /* Assistant */
    .stChatMessage[data-testid*="assistant"] {
        border-left: 4px solid #C74968 !important;
    }

    /* ===============================
    CHAT INPUT AREA (BOTTOM BAR)
    =============================== */
    [data-testid="stChatInput"] {
        background-color: #07070B !important;
        border-top: 1px solid rgba(255,255,255,0.06) !important;
    }

    [data-testid="stChatInput"] > div {
        background-color: #0E0E16 !important;
        border-radius: 14px !important;
        border: 2px solid transparent !important;
        background-image:
            linear-gradient(#0E0E16, #0E0E16),
            linear-gradient(135deg, #C77DFF, #C74968) !important;
        background-origin: border-box !important;
        background-clip: padding-box, border-box !important;
    }

    /* Text input */
    [data-testid="stChatInput"] input,
    [data-testid="stChatInput"] textarea {
        background-color: transparent !important;
        color: #E6E6F0 !important;
    }

    /* ===============================
    SEND BUTTON (KEEP DEFAULT ICON)
    =============================== */
    button[data-testid="stChatInputSubmitButton"] {
        background-color: #C74968 !important;
        border-radius: 10px !important;
        border: none !important;
    }

    button[data-testid="stChatInputSubmitButton"]:hover {
        background-color: #B33A58 !important;
    }

    button[data-testid="stChatInputSubmitButton"] svg {
        color: white !important;
        fill: white !important;
    }

    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #C77DFF 0%, #9D5DCF 50%, #C74968 100%) !important;
        border-right: 3px solid rgba(255, 255, 255, 0.1);
        box-shadow: 2px 0 20px rgba(199, 125, 255, 0.3);
    }

    /* Sidebar overlay for depth */
    [data-testid="stSidebar"]::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(180deg, 
            rgba(199, 125, 255, 0.1) 0%, 
            rgba(157, 93, 207, 0.05) 50%,
            rgba(199, 73, 104, 0.1) 100%);
        pointer-events: none;
    }
    /* ===============================
    SCROLLBAR (SUBTLE)
    =============================== */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #C77DFF, #C74968);
        border-radius: 6px;
    }

    /* Force user avatar to purple gradient */
    [data-testid="stChatMessageAvatarUser"] {
        background: linear-gradient(135deg, #C77DFF 0%, #B368EE 100%) !important;
    }
    
    /* Force assistant avatar to pink gradient */
    [data-testid="stChatMessageAvatarAssistant"] {
        background: linear-gradient(135deg, #C74968 0%, #B33A58 100%) !important;
    }
    
    /* Make sure icons are white */
    [data-testid="stChatMessageAvatarUser"] svg,
    [data-testid="stChatMessageAvatarAssistant"] svg {
        color: white !important;
    }
    
    [data-testid="stChatMessageAvatarUser"] path,
    [data-testid="stChatMessageAvatarAssistant"] path {
        fill: white !important;
    }
    
    </style>
    """,
        unsafe_allow_html=True,
    )



st.title("💬 HR Analytical Chatbot")
st.caption("Ask questions about the IBM HR Analytics dataset")


if "memory" not in st.session_state:
    st.session_state.memory = ChatMemory(max_turns=10)


with st.sidebar:
    st.header("Tools")

    provider = st.selectbox(
        "Model provider",
        ["local", "groq"],
        help="Local Falcon runs on CPU. Groq uses a cloud API (faster)."
    )

    transcript = st.session_state.memory.as_text()

    st.download_button(
        label="Download chat (TXT)",
        data=export_txt(transcript),
        file_name="chat_transcript.txt",
        mime="text/plain",
    )

    st.download_button(
        label="Download chat (PDF)",
        data=export_pdf(transcript),
        file_name="chat_transcript.pdf",
        mime="application/pdf",
    )


# Render chat history
for msg in st.session_state.memory.messages:
    with st.chat_message(msg.role):
        st.markdown(msg.content)

user_text = st.chat_input("Ask a question (e.g., attrition rate for overtime employees)...")

if user_text:
    st.session_state.memory.add("user", user_text)
    with st.chat_message("user"):
        st.markdown(user_text)

    answer = answer_question(user_text, provider=provider, conversation_history=st.session_state.memory.messages)

    st.session_state.memory.add("assistant", answer)
    with st.chat_message("assistant"):
        st.markdown(answer)
