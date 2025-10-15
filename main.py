# 🎓 Waha School Chatbot (AI-Powered, Arabic + English)
# Run using: streamlit run main.py

import streamlit as st
import PyPDF2
import os # <-- Necessary for reading environment variables
from deep_translator import GoogleTranslator
from openai import OpenAI
from dotenv import load_dotenv # <-- NEW IMPORT: To load the .env file

# Load environment variables (like OPENAI_API_KEY) from the local .env file
load_dotenv() 

# ------------------ API KEY SETUP (SECURELY) ------------------

# 1. Get the API key from the environment variable
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    # 2. Halt execution if the key is missing (secure fail)
    st.error("⚠️ FATAL ERROR: OpenAI API key (OPENAI_API_KEY) not found. Please ensure your .env file is correct.")
    st.stop()
    
# 3. Initialize the OpenAI client using the securely retrieved key
client = OpenAI(api_key=api_key)

# ------------------ PAGE SETUP ------------------
st.set_page_config(page_title="Waha School Chatbot", page_icon="🎓", layout="centered")

# ------------------ PDF READER ------------------
def read_pdf(file_path):
    text = ""
    if not os.path.exists(file_path):
        return f"Error: PDF file '{file_path}' not found."
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

pdf_data = read_pdf("school_data.pdf")

if "Error" in pdf_data:
    st.error(pdf_data)
    st.stop()

# ------------------ LANGUAGE TOGGLE ------------------
col1, col2 = st.columns([9, 1])
with col1:
    st.title("🎓 Waha School Chatbot")

if "language" not in st.session_state:
    st.session_state.language = "العربية"

with col2:
    if st.button("🌐", key="lang_button"):
        st.session_state.language = "English" if st.session_state.language == "العربية" else "العربية"

# ------------------ INTRO ------------------
if st.session_state.language == "English":
    st.write("Welcome! Ask me anything about the school 👇")
else:
    st.write("مرحباً! اسألني عن المدرسة 👇")

# ------------------ AI SEARCH ------------------
def ask_ai(question, pdf_text, lang):
    try:
        # If the interface is Arabic, translate the question to English (for better AI reasoning)
        if lang == "العربية":
            translated_q = GoogleTranslator(source='auto', target='en').translate(question)
        else:
            translated_q = question

        # Create a system prompt
        system_prompt = f"""
        You are an AI assistant for Waha School.
        Use ONLY the following school data to answer questions.
        If you don't find the answer, say you don't know.
        Keep answers polite and educational.
        ---
        SCHOOL DATA:
        {pdf_text}
        """

        # Send to AI model
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": translated_q}
            ],
            temperature=0.2
        )

        answer = response.choices[0].message.content.strip()

        # Translate back to Arabic if needed
        if lang == "العربية":
            answer = GoogleTranslator(source='en', target='ar').translate(answer)

        return answer

    except Exception as e:
        return "⚠️ خطأ أثناء معالجة الطلب." if lang == "العربية" else f"⚠️ Error: {e}"

# ------------------ CHAT INTERFACE ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if st.session_state.language == "English":
    input_prompt = "Ask me something about the school:"
    send_label = "Send"
else:
    input_prompt = "اسألني عن المدرسة:"
    send_label = "إرسال"

with st.form(key='chat_form', clear_on_submit=True):
    user_input = st.text_input(input_prompt)
    submitted = st.form_submit_button(send_label)

if submitted and user_input:
    lang = st.session_state.language
    answer = ask_ai(user_input, pdf_data, lang)

    st.session_state.messages.insert(0, ("🤖 Waha", answer))
    st.session_state.messages.insert(0, ("🧍‍♀️ You", user_input))

# ------------------ DISPLAY ------------------
for sender, msg in st.session_state.messages:
    color = "#eaf2fd" if sender == "🧍‍♀️ You" else "#f0f0f0"
    st.markdown(
        f"<div style='background-color:{color};padding:10px;border-radius:10px;margin:5px 0;'><b>{sender}:</b> {msg}</div>",
        unsafe_allow_html=True,
    )

# ------------------ FOOTER ------------------
st.markdown("<hr><center>© 2025 Waha School Chatbot | Created by Fatima Al Naseri</center>", unsafe_allow_html=True)
