# 🎓 Waha School Chatbot (Arabic Data, Final)
# Run using: streamlit run main.py

import streamlit as st
import PyPDF2
import os
import re # Added for advanced keyword matching
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
            search_query_ar = translator_en_to_ar.translate(text=question).lower()
        
        # Clean the query (remove non-Arabic, non-digit characters)
        search_query_ar_cleaned = re.sub(r'[^\u0600-\u06FF\s\d]', '', search_query_ar).strip()
        
        # 2. Extract and Prepare Sentences for Search
        # FIXED: Use the period/full stop (.) as the reliable sentence separator for Arabic text
        sentences = text.replace('\n', ' ').replace('\r', '').split(".")
        
        best_score = -1
        found_sentence_ar = None

        # Prepare keywords: use a dictionary to map common search terms to the expected PDF terms
        # This acts as a simple form of synonym/stemming mapping
        keyword_map = {
            'المديرة': 'مديرة المدرسة',
            'مدير': 'مديرة المدرسة',
            'الاخصائية': 'أخصائية الصف',
            'اخصائية': 'أخصائية الصف',
            'مريم': 'مريم الشامسي',
            'عليا': 'عليا الكويتي',
            'موزة': 'معلمة موزة',
            'عاشر': ['عاشر', '10'], 
            'حادي': ['حادي عشر', '11'], 
            'ثاني': ['ثاني عشر', '12'],
            'الثاني': ['ثاني عشر', '12'],
        }

        # Break down the cleaned query into core terms
        query_terms = search_query_ar_cleaned.split()

        # 3. Iterate and Score using Advanced Matching
        for sentence in sentences:
            sentence_ar_cleaned = re.sub(r'[^\u0600-\u06FF\s\d]', '', sentence).strip()
            if not sentence_ar_cleaned:
                continue

            current_score = 0
            
            # Use regex to search for the presence of mapped keywords and grade numbers
            # This is more resilient than simple substring matching
            
            # Score 1: Check for the main subject (e.g., 'مديرة' or 'أخصائية')
            subject_found = False
            for term in ['مديرة', 'أخصائية']:
                if re.search(term, sentence_ar_cleaned):
                    current_score += 1
                    subject_found = True
                    break
            
            # Score 2: Check for specific entity name or grade
            if subject_found:
                for term in query_terms:
                    # Look up if the term has a mapping (e.g., 'عاشر' maps to 'عاشر' or '10')
                    mapped_terms = keyword_map.get(term, [term])
                    
                    for mapped_term in mapped_terms:
                        if re.search(re.escape(mapped_term), sentence_ar_cleaned):
                            current_score += 1 # Add score for finding the grade or name
                            break # Move to next query term

            # Update the best match
            if current_score > best_score and sentence.strip():
                best_score = current_score
                found_sentence_ar = sentence.strip()

        # 4. Final Output Translation
        # Require a minimum score of 2 (Subject + Grade/Name)
        if best_score >= 2:
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
        placeholder="e.g., What are the school hours?" if st.session_state.language == "English" else "مثل: ما هي ساعات الدوام المدرسي؟"
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
