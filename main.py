# 🎓 Waha School Chatbot (with PDF data)
# Created by Fatima Al Naseri
# Run using: streamlit run main.py

import streamlit as st
import PyPDF2
import os
from deep_translator import GoogleTranslator
import re # <-- New import for better search

# ------------------ PAGE SETUP ------------------
st.set_page_config(page_title="Waha School Chatbot", page_icon="🎓", layout="centered")


# ------------------ PDF READER ------------------
def read_pdf(file_path):
    text = ""
    if not os.path.exists(file_path):
        return f"Error: PDF file '{file_path}' not found. Make sure it's in the main folder."

    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                # Extracting text might result in poor formatting, but we handle it in find_answer
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"


# Load your school PDF here
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
    st.session_state.language = "العربية" # Default to Arabic

with col2:
    if st.button("🌐", key="lang_button"):
        st.session_state.language = "العربية" if st.session_state.language == "English" else "English"

# ------------------ INTRO ------------------
if st.session_state.language == "English":
    st.write("Welcome! Ask me about the school. Type below 👇")
else:
    st.write("مرحباً! اسألني عن المدرسة. اكتب سؤالك بالأسفل 👇")


# ------------------ FIND ANSWER (ENHANCED SEARCH LOGIC) ------------------
def find_answer(question, text):
    try:
        # 1. Translate the input question to English for searching the PDF
        input_translator = GoogleTranslator(source='auto', target='en')
        search_question = input_translator.translate(text=question)

        # 2. Determine the final answer language
        target_lang_code = 'ar' if st.session_state.language == 'العربية' else 'en'


        # --- CHATBOT SEARCH LOGIC ---
        search_question = search_question.lower()
        
        # Split text into lines/sections using newline characters
        lines = text.split('\n') 

        # Simplified keyword extraction (prioritize "name", "school", "hours", "contact")
        stop_words = ["what", "is", "the", "are", "of", "a", "an", "how", "when", "where", "me", "about", "tell", "who", "for", "i'm", "i", "do", "you", "and"]
        keywords = [word for word in search_question.split() if word not in stop_words and len(word) > 2]

        # Add proper nouns/search terms for high-value queries
        if 'name' in search_question and 'school' in search_question:
             keywords.append('مدرسة') # Search for the Arabic word for school in the extracted text
             keywords.append('اسم')   # Search for the Arabic word for name in the extracted text

        found_text_en = None
        
        # Loop through keywords to find the best match in the extracted lines
        for keyword in set(keywords):
            # Check for a match in the original PDF text
            for line in lines:
                # We check against the original line (which is mostly Arabic in your case)
                if keyword.lower() in line.lower() or keyword.strip() in line.lower():
                    # Prioritize exact lines for facts like 'school name'
                    found_text_en = line.strip()
                    break
            if found_text_en:
                break # Found a match, stop searching keywords

        
        if found_text_en:
            # 3. Translate the found (likely Arabic) text to English first for a clean answer, 
            #    THEN translate back to the target language (Arabic or English).
            
            # Use 'auto' source language since the extracted text might be a mix of English/Arabic/garbage
            translation_to_english = GoogleTranslator(source='auto', target='en')
            # The found line might be Arabic, so translate it to English first
            found_text_en_clean = translation_to_english.translate(text=found_text_en)

            # 4. Translate the clean English text back to the user's target language
            if target_lang_code != 'en':
                output_translator = GoogleTranslator(source='en', target=target_lang_code)
                final_answer = output_translator.translate(text=found_text_en_clean)
            else:
                final_answer = found_text_en_clean
            
            return final_answer

        return None # No answer found

    except Exception as e:
        if st.session_state.language == 'العربية':
            return "عذراً، حدث خطأ في الترجمة أو في عملية البحث."
        else:
            return f"Search/Translation Error: Could not process the request."


# ------------------ CHAT ------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Dynamic Prompt Variables ---
if st.session_state.language == "English":
    input_prompt = "Ask me something about the school:"
    send_label = 'Send'
else:
    input_prompt = "اسألني عن المدرسة:"
    send_label = 'إرسال'

# Input and Submission
with st.form(key='chat_form', clear_on_submit=True):
    user_input = st.text_input(
        input_prompt, 
        key="user_query_input",
        placeholder="e.g., What are the school hours?" if st.session_state.language == "English" else "مثل: ما هي ساعات الدوام المدرسي؟"
    )

    submit_button = st.form_submit_button(label=send_label) 

if submit_button and user_input:
    # --- FIND ANSWER LOGIC ---
    answer = find_answer(user_input, pdf_data)

    # Handle case where no answer is found OR a translation error occurs
    if not answer or answer.startswith("عذراً، حدث خطأ") or answer.startswith("Search/Translation Error"):
        if st.session_state.language == "English":
            answer = "I'm sorry, I couldn't find that in the school information."
        else:
            answer = "عذراً، لم أجد هذه المعلومة في ملف المدرسة."

    # --- SAVE TO HISTORY ---
    st.session_state.messages.insert(0, ("🤖 Waha", answer))
    st.session_state.messages.insert(0, ("🧍‍♀️ You", user_input))


# ------------------ DISPLAY ------------------
# Display messages in the order they were inserted (newest at the top)
for sender, msg in st.session_state.messages: 
    color = "#eaf2fd" if sender == "🧍‍♀️ You" else "#f0f0f0"
    
    # Determine text direction for Arabic
    is_arabic_response = st.session_state.language == 'العربية' and sender == '🤖 Waha'
    direction = "rtl" if is_arabic_response else "ltr"
    text_align = "right" if is_arabic_response else "left"
    
    st.markdown(
        f"<div style='background-color:{color};padding:10px;border-radius:10px;margin:5px 0; word-break: break-word; text-align:{text_align}; direction:{direction};'><b>{sender}:</b> {msg}</div>",
        unsafe_allow_html=True)

# ------------------ FOOTER ------------------

st.markdown("<hr><center>© 2025 Waha School Chatbot | Created by Fatima Al Naseri</center>", unsafe_allow_html=True)
