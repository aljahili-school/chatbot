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


# ------------------ FIND ANSWER (SEARCHES PDF DATA) ------------------
def find_answer(question, pdf_text, user_is_arabic):
    try:
        search_query_ar = question.lower()
        
        # 1. Prepare the Search Query (Must be in Arabic to match the facts)
        if not user_is_arabic:
            # If input is English, translate it to Arabic for searching
            translator_en_to_ar = GoogleTranslator(source='en', target='ar')
            search_query_ar = translator_en_to_ar.translate(text=question).lower()
        
        # Clean the query (remove most non-Arabic, non-digit characters)
        search_query_ar_cleaned = re.sub(r'[^\u0600-\u06FF\s\d]', '', search_query_ar).strip()
        
        # 2. CRITICAL CLEANING AND SPLITTING STEP
        # We split the raw text by the period (.) and then clean each segment
        raw_facts_list = pdf_text.replace('\n', ' ').replace('\r', '').split(".")
        
        # Filter and clean the list of facts
        facts_list = []
        for fact in raw_facts_list:
            cleaned_fact = fact.strip()
            if len(cleaned_fact) > 5: # Ignore very short, likely junk segments
                facts_list.append(cleaned_fact + '.') # Add period back for cleaner display if needed

        
        best_score = -1
        found_fact_ar = None

        # Define comprehensive keyword mapping
        required_segments = {
            'مديرة المدرسة': ['مديرة', 'مدير', 'principal'],
            'أخصائية الصف الثاني عشر': ['أخصائية', 'الصف الثاني عشر', '12', 'ثاني عشر', 'social worker'],
            'أخصائية الصف الحادي عشر': ['أخصائية', 'الصف الحادي عشر', '11', 'حادي عشر', 'social worker'],
            'أخصائية الصف العاشر': ['أخصائية', 'الصف العاشر', '10', 'عاشر', 'social worker'],
        }

        # 3. Iterate and Score by checking for required segments
        for fact in facts_list:
            current_score = 0
            
            # Clean the fact for robust searching
            fact_cleaned_for_search = re.sub(r'[^\u0600-\u06FF\s\d]', '', fact).strip()

            # Check for a near-perfect match on the main subject part of the fact
            fact_subject = fact.split('هي')[0].strip()
            if re.search(re.escape(fact_subject), search_query_ar_cleaned):
                current_score = 100 # Perfect match score

            # If not a perfect match, check if this fact is relevant based on segments
            if current_score < 100:
                # Find the key segment for this fact (e.g., 'مديرة المدرسة')
                for segment_key, synonyms in required_segments.items():
                    if fact.startswith(segment_key):
                        # Score this fact based on how many synonyms are in the user's query
                        for syn in synonyms:
                            if re.search(re.escape(syn), search_query_ar_cleaned):
                                current_score += 1
                        break

            # Prioritize the fact with the highest score
            if current_score > best_score:
                best_score = current_score
                found_fact_ar = fact.strip()

        # 4. Final Output Translation
        if found_fact_ar and best_score > 0:
            if user_is_arabic:
                # Answer is already in Arabic
                final_answer = found_fact_ar
            else:
                # Translate Arabic result back to English
                translator_ar_to_en = GoogleTranslator(source='ar', target='en')
                final_answer = translator_ar_to_en.translate(text=found_fact_ar)
            
            # Ensure punctuation
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
