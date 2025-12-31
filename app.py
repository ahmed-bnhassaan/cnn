# app.py

import streamlit as st
from services import extract_text_from_pdf, generate_mcq

st.set_page_config(page_title="MCQ Chatbot", layout="wide")
st.title("🤖 MCQ Generator Chatbot")

# --- Session state init ---
if "chat" not in st.session_state:
    st.session_state.chat = []
if "history" not in st.session_state:
    st.session_state.history = []
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "num_questions" not in st.session_state:
    st.session_state.num_questions = 5
if "num_pages" not in st.session_state:
    st.session_state.num_pages = 1
if "pdf_uploaded" not in st.session_state:
    st.session_state.pdf_uploaded = False
if "total_pages" not in st.session_state:
    st.session_state.total_pages = 1

# --- Sidebar: Upload + Settings ---
with st.sidebar:
    st.header("📂 Upload PDF (optional)")
    pdf_file = st.file_uploader("Choose a PDF file", type="pdf")

    if pdf_file:
        import pdfplumber
        try:
            with pdfplumber.open(pdf_file) as pdf:
                total = len(pdf.pages)
                st.session_state.total_pages = total
        except:
            st.error("⚠️ Error reading PDF.")

        st.session_state.num_pages = st.number_input(
            "📄 Number of pages to read",
            min_value=1,
            max_value=st.session_state.total_pages,
            value=min(3, st.session_state.total_pages)
        )

        st.session_state.num_questions = st.number_input(
            "📝 Number of MCQs",
            min_value=1,
            max_value=50,
            value=5
        )

        # extract PDF text immediately
        st.session_state.pdf_text = extract_text_from_pdf(pdf_file, st.session_state.num_pages)
        st.session_state.pdf_uploaded = True
        st.success("✅ PDF uploaded and text extracted.")

    st.divider()
    st.header("🕓 Chat History")
    for i, msg in enumerate(st.session_state.history):
        st.markdown(f"**{i+1}.** {msg[:50]}...")

    st.divider()
    if st.button("❌ End Session"):
        st.session_state.clear()
        st.experimental_rerun()

# --- Show previous messages ---
for sender, msg in st.session_state.chat:
    with st.chat_message(sender):
        st.markdown(msg)

# --- Chat input (always visible) ---
user_input = st.chat_input("Type your message (e.g., 'generate questions')")

if user_input:
    st.session_state.chat.append(("user", user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    # --- Only try to generate if PDF is uploaded ---
    if "generate" in user_input.lower() and "question" in user_input.lower():
        if not st.session_state.pdf_uploaded:
            error_msg = "⚠️ Please upload a PDF file first."
            st.session_state.chat.append(("assistant", error_msg))
            with st.chat_message("assistant"):
                st.markdown(error_msg)
        else:
            with st.chat_message("assistant"):
                st.markdown("Generating questions...")

            response = generate_mcq(
                st.session_state.pdf_text[:1500],
                st.session_state.num_questions
            )

            st.session_state.chat.append(("assistant", response))
            st.session_state.history.append(response)

            with st.chat_message("assistant"):
                st.markdown(response)

                # ✅ Add download button inside chat
                st.download_button(
                    label="💾 Download Questions as .txt",
                    data=response.encode("utf-8"),
                    file_name="mcq_questions.txt",
                    mime="text/plain"
                )

    else:
        fallback = "❓ Please say something like 'generate questions'."
        st.session_state.chat.append(("assistant", fallback))
        with st.chat_message("assistant"):
            st.markdown(fallback)
