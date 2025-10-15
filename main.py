# 🎓 Waha School Chatbot (Arabic Data, Final)
# Run using: streamlit run main.py

import streamlit as st
import PyPDF2
import os
import re 
from deep_translator import GoogleTranslator

# ------------------ PAGE SETUP ------------------
st.set_page_config(page_title="Waha School Chatbot", page_icon="🎓", layout="centered")


# ------------------ PDF READER ------------------
def read_pdf(file_path):
    text = ""
    # Assuming school_data.pdf now contains content in Arabic.
    if not os.path.exists(file_path):
        return f"Error: PDF file '{file_path}' not found. Make sure it's in the main folder."

    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                # PyPDF2 extracts raw text, which needs careful handling for Arabic.
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"


# Load your school PDF here
# *** NOTE: The file 'school_data.pdf' is now assumed to contain ARABIC content. ***
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
    st.session_state.language = "العربية" # Default language is Arabic

with col2:
    # Button to switch UI language
    if st.button("🌐", key="lang_button"):
        st.session_state.language = "العربية" if st.session_state.language == "English" else "English"

# ------------------ INTRO ------------------
if st.session_state.language == "English":
    st.write("Welcome! Ask me about the school. Type below 👇")
    user_lang_is_arabic = False
else:
    st.write("مرحباً! اسألني عن المدرسة. اكتب سؤالك بالأسفل 👇")
    user_lang_is_arabic = True


# ------------------ FIND ANSWER (SEARCHES ARABIC PDF) ------------------
def find_answer(question, text, user_is_arabic):
    try:
        search_query_ar = question.lower()
        
        # 1. Prepare the Search Query (Must be in Arabic to match the PDF)
        if not user_is_arabic:
            # If input is English, translate it to Arabic for searching the Arabic PDF
            translator_en_to_ar = GoogleTranslator(source='en', target='ar')
            # Translate and remove punctuation to handle variations like "social worker?" vs "social worker"
            search_query_ar = translator_en_to_ar.translate(text=question).lower()
        
        # Clean the query (remove most non-Arabic, non-digit characters)
        search_query_ar_cleaned = re.sub(r'[^\u0600-\u06FF\s\d]', '', search_query_ar).strip()
        
        # 2. Extract and Prepare Sentences for Search
        # Use the period/full stop (.) as the reliable sentence separator for Arabic text
        sentences = text.replace('\n', ' ').replace('\r', '').split(".")
        
        # Define comprehensive keyword list for scoring
        # This list includes all roles, names, and grade numbers from the PDF content
        keywords_pdf = [
            'مديرة المدرسة', 'أخصائية الصف', 'مريم الشامسي', 'عليا الكويتي', 'معلمة موزة',
            'عاشر', '10', 'حادي عشر', '11', 'ثاني عشر', '12', 'فاطمة الناصري'
        ]

        # 3. Iterate and Score using strict presence check
        best_score = -1
        found_sentence_ar = None
        query_words = search_query_ar_cleaned.split()

        for sentence in sentences:
            sentence_ar_cleaned = re.sub(r'[^\u0600-\u06FF\s\d]', '', sentence).strip()
            if not sentence_ar_cleaned:
                continue

            current_score = 0
            
            # Count how many of the PDF's official keywords appear in the cleaned sentence
            for kw in keywords_pdf:
                # Use regex word boundaries to ensure we match whole words or numbers, not just substrings
                if re.search(r'\b' + re.escape(kw) + r'\b', sentence_ar_cleaned):
                    current_score += 1
            
            # Crucial filtering: The sentence must contain at least one major role keyword (مديرة or أخصائية) 
            # and it must match at least one word from the user's input.
            role_match = re.search(r'مديرة|أخصائية', sentence_ar_cleaned)
            
            if role_match and current_score > best_score:
                # To ensure relevance, we must also check if the user's input words are *present* in the sentence.
                # This prevents giving a random answer if the sentence just happens to contain a high-scoring but irrelevant word.
                relevance_score = 0
                for q_word in query_words:
                    if re.search(re.escape(q_word), sentence_ar_cleaned):
                        relevance_score += 1
                
                # We update the best match if it has a high score AND is relevant to the user's query
                if relevance_score > 0 and current_score > best_score:
                    best_score = current_score
                    found_sentence_ar = sentence.strip()

        # 4. Final Output Translation
        # Require a minimum score of 1 and a role match (already filtered above)
        if found_sentence_ar:
            if user_is_arabic:
                # Answer is already in Arabic (from the PDF)
                final_answer = found_sentence_ar
            else:
                # Translate Arabic result back to English
                translator_ar_to_en = GoogleTranslator(source='ar', target='en')
                final_answer = translator_ar_to_en.translate(text=found_sentence_ar)
            
            # Simple check to ensure punctuation
            if final_answer and not final_answer.strip().endswith(('.', '?', '!', '؟')):
                return final_answer.strip() + "."
            
            return final_answer.strip()

        return None # No answer found

    except Exception as e:
        # Provide language-appropriate error message
        print(f"Error during search: {e}") # Debugging
        if user_is_arabic:
            return "عذراً، حدث خطأ في معالجة الطلب. يرجى المحاولة مرة أخرى."
        else:
            return "Error: Could not process the request. Please try again."


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
        placeholder="e.g., Who is the school principal?" if st.session_state.language == "English" else "مثل: من هي مديرة المدرسة؟"
    )

    submit_button = st.form_submit_button(label=f'{send_label} / {send_label}') 

if submit_button and user_input:
    # --- Determine if the UI is currently set to Arabic ---
    is_arabic_ui = (st.session_state.language == "العربية")
    
    # --- FIND ANSWER LOGIC ---
    answer = find_answer(user_input, pdf_data, is_arabic_ui)

    # Handle case where no answer is found
    if not answer:
        if st.session_state.language == "English":
            answer = "I'm sorry, I couldn't find that information in the school's document."
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
