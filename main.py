# 🎓 Waha School Chatbot (with PDF data)
# Created by Fatima Al Naseri
# Run using: streamlit run school_chatbot.py

import streamlit as st
import PyPDF2
import os
from deep_translator import GoogleTranslato

# Initialize Translator outside of functions for efficiency
translator = GoogleTranslator()

# ------------------ PAGE SETUP ------------------
st.set_page_config(page_title="Waha School Chatbot", page_icon="🎓", layout="centered")


# ------------------ PDF READER ------------------
def read_pdf(file_path):
    text = ""
    if not os.path.exists(file_path):
        return f"Error: PDF file '{file_path}' not found in the same folder."

    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"


# Load your school PDF here (assuming English data)
pdf_data = read_pdf("school_data.pdf")

# Check if the PDF loaded successfully
if "Error" in pdf_data and pdf_data.startswith("Error:"):
    st.error(pdf_data)
    st.stop()

# ------------------ PAGE HEADER ------------------
col1, col2 = st.columns([9, 1])
with col1:
    st.title("🎓 Waha School Chatbot")

# Language toggle logic
if "language" not in st.session_state:
    st.session_state.language = "English"

with col2:
    if st.button("🌐", key="lang_button"):
        st.session_state.language = "العربية" if st.session_state.language == "English" else "English"

# ------------------ INTRO ------------------
if st.session_state.language == "English":
    st.write("Welcome! Ask me about the school. Type below 👇")
else:
    st.write("مرحباً! اسألني عن المدرسة. اكتب سؤالك بالأسفل 👇")


# ------------------ FIND ANSWER (MODIFIED FOR TRANSLATION) ------------------
def find_answer(question, text):
    try:
        # 1. Detect language of the question
        detected_lang = translator.detect(question).lang

        # 2. Translate question to English if needed (assuming PDF data is English)
        if detected_lang != 'en':
            # Translate to English for searching the English PDF data
            search_question = translator.translate(question, dest='en').text
        else:
            search_question = question

        search_question = search_question.lower()
        sentences = text.replace('\n', ' ').replace('\r', '').split(". ")

        stop_words = ["what", "is", "the", "are", "of", "a", "an", "how", "when", "where", "me", "about", "tell"]
        keywords = [word for word in search_question.split() if word not in stop_words]

        # Simple matching: Return the first English sentence that contains one or more English keywords
        found_sentence_en = None
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in keywords):
                found_sentence_en = sentence.strip() + "."
                break

        if found_sentence_en:
            # 3. Translate the found English answer back to the original question language
            if detected_lang != 'en':
                # Translate back to the user's language (e.g., Arabic)
                final_answer = translator.translate(found_sentence_en, dest=detected_lang).text
            else:
                final_answer = found_sentence_en

            return final_answer

        return None  # No answer found

    except Exception as e:
        st.warning(f"Translation Error: {e}")
        return None


# ------------------ CHAT ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# Input and Submission are placed inside a form to clear the input field after submission
with st.form(key='chat_form', clear_on_submit=True):
    user_input = st.text_input(
        "Ask me something about the school / اسألني عن المدرسة:",
        key="user_query_input",
        placeholder="e.g., What are the school hours?" if st.session_state.language == "English" else "مثل: ما هي ساعات الدوام المدرسي؟"
    )

    submit_button = st.form_submit_button(label='Send / إرسال')

if submit_button and user_input:
    # --- FIND ANSWER LOGIC ---
    answer = find_answer(user_input, pdf_data)

    # Handle case where no answer is found OR a translation error occurs
    if not answer:
        if st.session_state.language == "English":
            answer = "I'm sorry, I couldn't find that in the school information."
        else:
            answer = "عذراً، لم أجد هذه المعلومة في ملف المدرسة."

    # --- SAVE TO HISTORY ---
    st.session_state.messages.append(("🧍‍♀️ You", user_input))
    st.session_state.messages.append(("🤖 Waha", answer))

# ------------------ DISPLAY ------------------
for sender, msg in st.session_state.messages:
    color = "#eaf2fd" if sender == "🧍‍♀️ You" else "#f0f0f0"
    st.markdown(
        f"<div style='background-color:{color};padding:10px;border-radius:10px;margin:5px 0; word-break: break-word;'><b>{sender}:</b> {msg}</div>",
        unsafe_allow_html=True)

# ------------------ FOOTER ------------------

st.markdown("<hr><center>© 2025 Waha School Chatbot | Created by Fatima Al Naseri</center>", unsafe_allow_html=True)
