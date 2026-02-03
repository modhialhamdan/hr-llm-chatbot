import sys
from pathlib import Path

# Add project root to PYTHONPATH for Streamlit
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

import streamlit as st
from src.chat.memory import ChatMemory
from src.chat.router import answer_question

st.set_page_config(page_title="HR Analytics Chatbot", page_icon="💬", layout="centered")

st.title("💬 HR Analytics Chatbot")
st.caption("Ask questions about the IBM HR Analytics dataset (SQLite-backed).")

if "memory" not in st.session_state:
    st.session_state.memory = ChatMemory(max_turns=10)

# render history
for msg in st.session_state.memory.messages:
    with st.chat_message(msg.role):
        st.markdown(msg.content)

user_text = st.chat_input("Ask a question (e.g., attrition rate for overtime employees)...")

if user_text:
    st.session_state.memory.add("user", user_text)
    with st.chat_message("user"):
        st.markdown(user_text)

    answer = answer_question(user_text)
    st.session_state.memory.add("assistant", answer)
    with st.chat_message("assistant"):
        st.markdown(answer)
