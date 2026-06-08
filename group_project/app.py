import streamlit as st
import sys
from pathlib import Path

# Add project root to path so we can import modules cleanly
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from group_project.src.rag_pipeline import ask_question

# ---- UI Configuration ----
st.set_page_config(page_title="Vietnam Drug Law Chatbot", page_icon="⚖️")
st.title("⚖️ Drug Law & News RAG Chatbot")
st.markdown("Hỏi đáp về Luật Phòng, chống ma túy Việt Nam và các tin tức liên quan.")

# ---- Initialize Session State for Chat History ----
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---- Render Chat History ----
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        # Optionally render sources if present
        if "sources" in msg and msg["sources"]:
            st.caption(f"📚 Nguồn tham khảo: {', '.join(msg['sources'])}")

# ---- Chat Input & Processing ----
if prompt := st.chat_input("Nhập câu hỏi của bạn về luật ma túy..."):
    # 1. Add user message to state and display it
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Call RAG Pipeline
    with st.chat_message("assistant"):
        with st.spinner("Đang tra cứu tài liệu và phân tích..."):
            # Call pipeline. We pass session_state.messages if we want to build context later,
            # but currently ask_question uses a lightweight memory interface.
            result = ask_question(question=prompt, chat_history=st.session_state.messages)
            
            answer = result.get("answer", "")
            sources = result.get("sources", [])
            contexts_used = result.get("contexts_used", 0)
            error = result.get("error")
            
            # Format the output
            if error:
                display_text = f"❌ **Đã xảy ra lỗi:** {error}"
            else:
                display_text = answer
                # Fallback handler logic
                if answer == "I cannot verify this information" or contexts_used == 0:
                    display_text += "\n\n*(Lưu ý: Hệ thống hiện không có tài liệu/bằng chứng phù hợp để trả lời câu hỏi này. Có thể do tài liệu chưa được upload lên PageIndex hoặc đã đạt giới hạn quota.)*"

            # Render the answer
            st.markdown(display_text)
            
            # Render sources neatly
            if sources:
                st.caption(f"📚 Nguồn tham khảo: {', '.join(sources)}")
        
        # 3. Add assistant response to state
        st.session_state.messages.append({
            "role": "assistant",
            "content": display_text,
            "sources": sources
        })
