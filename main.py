# 🎓 Waha School Chatbot (with PDF data)
# Created by Fatima Al Naseri
# Run using: streamlit run main.py

import streamlit as st
import PyPDF2
import os
from deep_translator import GoogleTranslator

# ------------------ PAGE SETUP ------------------
st.set_page_config(page_title="Waha School Chatbot", page_icon="🎓", layout="centered")


# ------------------ PDF READER ------------------
def read_pdf(file_path):
    text = ""
    # In Streamlit Cloud, the file path is just the name if it's in the root of the repo
    # *** IMPORTANT: Change the file name here if you renamed your PDF to fix caching! ***
    if not os.path.exists(file_path):
        return f"Error: PDF file '{file_path}' not found. Make sure it's in the main folder."

    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"


# Load your school PDF here
# *** IMPORTANT: Use the correct, clean PDF file name here ***
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


# ------------------ FIND ANSWER (FIXED LOGIC) ------------------
def find_answer(question, text):
    try:
        # 1. Translate the input question to English for searching the PDF
        input_translator = GoogleTranslator(source='auto', target='en')
        search_question = input_translator.translate(text=question).lower()

        # 2. Determine the final answer language based on the Streamlit toggle
        target_lang_code = 'ar' if st.session_state.language == 'العربية' else 'en'


        # --- CHATBOT SEARCH LOGIC: FIXED TO USE SCORING ---
        # Split text into sentences using '. ' as the delimiter
        sentences = text.replace('\n', ' ').replace('\r', '').split(". ")

        # Simplified keyword extraction: keeping important nouns and the number '10'
        stop_words = ["what", "is", "the", "are", "of", "a", "an", "how", "when", "where", "me", "about", "tell", "who", "for", "i'm", "i", "do", "you"]
        # Include numbers and single letters if they are part of the grade (e.g., '10', '9')
        keywords = [word for word in search_question.split() if word not in stop_words and len(word) > 1]
        
        # Variables for best match
        best_score = -1
        found_sentence_en = None

        # Iterate through all sentences to find the one with the highest keyword overlap (score)
        for sentence in sentences:
            sentence_lower = sentence.lower()
            current_score = 0
            
            # Calculate score: count how many keywords are present
            for keyword in keywords:
                if keyword in sentence_lower:
                    current_score += 1
            
            # Update the best match if the current sentence has a higher score
            if current_score > best_score:
                best_score = current_score
                found_sentence_en = sentence.strip() + "."
        
        
        # Only return an answer if a good match (score of 2 or more) was found
        if best_score >= 2:
            # 3. Translate the found English answer back to the user's language
            if target_lang_code != 'en':
                # Initialize translator for output: source English, target user's language
                output_translator = GoogleTranslator(source='en', target=target_lang_code)
                final_answer = output_translator.translate(text=found_sentence_en)
            else:
                final_answer = found_sentence_en

            return final_answer

        return None  # No answer found with a sufficient score

    except Exception as e:
        # If translation fails, provide a language-appropriate error message
        if st.session_state.language == 'العربية':
            return "عذراً، حدث خطأ في الترجمة. يرجى المحاولة مرة أخرى."
        else:
            return f"Translation Error: Could not process the request."


# ------------------ CHAT ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Dynamic Prompt Variable ---
if st.session_state.language == "English":
    input_prompt = "Ask me something about the school:"
    send_label = 'Send'
else:
    input_prompt = "اسألني عن المدرسة:"
    send_label = 'إرسال'

# Input and Submission are placed inside a form to clear the input field after submission
with st.form(key='chat_form', clear_on_submit=True):
    user_input = st.text_input(
        input_prompt, 
        key="user_query_input",
        placeholder="e.g., What are the school hours?" if st.session_state.language == "English" else "مثل: ما هي ساعات الدوام المدرسي؟"
    )

    submit_button = st.form_submit_button(label=f'{send_label} / {send_label}') 

if submit_button and user_input:
    # --- FIND ANSWER LOGIC ---
    answer = find_answer(user_input, pdf_data)

    # Handle case where no answer is found OR a translation error occurs
    if not answer or answer.startswith("عذراً، حدث خطأ") or answer.startswith("Translation Error"):
        if st.session_state.language == "English":
            answer = "I'm sorry, I couldn't find that in the school information."
        else:
            answer = "عذراً، لم أجد هذه المعلومة في ملف المدرسة."

    # --- SAVE TO HISTORY ---
    # Insert the newest interaction to the front of the list
    st.session_state.messages.insert(0, ("🤖 Waha", answer))
    st.session_state.messages.insert(0, ("🧍‍♀️ You", user_input))


# ------------------ DISPLAY ------------------
# Display messages in the order they were inserted (newest at the top)
for sender, msg in st.session_state.messages: 
    color = "#eaf2fd" if sender == "🧍‍♀️ You" else "#f0f0f0"
    st.markdown(
        f"<div style='background-color:{color};padding:10px;border-radius:10px;margin:5px 0; word-break: break-word;'><b>{sender}:</b> {msg}</div>",
        unsafe_allow_html=True)

# ------------------ FOOTER ------------------

st.markdown("<hr><center>© 2025 Waha School Chatbot | Created by Fatima Al Naseri</center>", unsafe_allow_html=True)
