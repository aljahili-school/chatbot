# 🎓 Waha School Chatbot (with CSV data)
# Created by Fatima Al Naseri
# Run using: streamlit run main.py

import streamlit as st
import pandas as pd             # <-- NEW: For reading the CSV file
from deep_translator import GoogleTranslator
import re                       # For slightly more advanced text matching

# ------------------ PAGE SETUP ------------------
st.set_page_config(page_title="Waha School Chatbot", page_icon="🎓", layout="centered")


# ------------------ CSV READER ------------------
def load_data(file_path="school_data.csv"):
    """Loads the school data from a CSV file into a pandas DataFrame."""
    try:
        # Load the CSV file. Replace any NaN (missing) values with an empty string for safety.
        data_frame = pd.read_csv(file_path).fillna('')
        
        # Ensure the essential columns exist
        required_cols = ['Role', 'Name', 'Contact Detail']
        if not all(col in data_frame.columns for col in required_cols):
             st.error(f"Error: CSV file must contain columns: {', '.join(required_cols)}")
             st.stop()
        
        # Convert all relevant text columns to lowercase for case-insensitive searching later
        data_frame['Role_lower'] = data_frame['Role'].str.lower()
        
        return data_frame
    except FileNotFoundError:
        st.error(f"Error: CSV file '{file_path}' not found. Make sure it's uploaded to GitHub.")
        st.stop()
    except Exception as e:
        st.error(f"Error loading CSV data: {str(e)}")
        st.stop()

# Load the data once at the start
school_data_df = load_data()


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


# ------------------ FIND ANSWER (NEW CSV LOGIC) ------------------
def find_answer(question, df):
    """Searches the DataFrame for keywords matching the user's question."""
    try:
        # 1. Translate the input question to English for searching the data
        input_translator = GoogleTranslator(source='auto', target='en')
        search_question_en = input_translator.translate(text=question).lower()

        # 2. Determine the final answer language
        target_lang_code = 'ar' if st.session_state.language == 'العربية' else 'en'
        
        # --- CHATBOT SEARCH LOGIC: Match by Keyword in the 'Role_lower' column ---
        
        # List of expected keywords (can be expanded)
        keywords = ["principal", "social worker", "hours", "phone", "email", "grade 10", "grade 12"]
        
        # Look for a specific keyword from the question that is in the Role column
        # Using a regex word boundary (\b) for better matching (e.g., matching "phone" but not "telephone")
        
        # Combine keywords to form a regex search pattern
        pattern = r'\b(' + '|'.join(re.escape(k) for k in keywords) + r')\b'
        
        # Filter the DataFrame: Find rows where the Role column contains one of the keywords
        results = df[df['Role_lower'].str.contains(pattern, case=False, na=False)]
        
        if not results.empty:
            response_parts = []
            
            # Use the first English row for translation base
            for index, row in results.iterrows():
                role = row['Role']
                name = row['Name']
                detail = row['Contact Detail']
                contact_type = row['Contact Type'] if 'Contact Type' in row.index else ''
                
                # Format the structured English response
                if detail:
                    # Generic staff/info response
                    response_parts.append(f"{role} is: {name}. The contact detail is {detail} ({contact_type}).")
                else:
                    # If contact detail is missing
                     response_parts.append(f"{role} is: {name}.")
                     
            found_answer_en = "\n".join(response_parts)
            
            # 3. Translate the found English answer back to the user's language
            if target_lang_code != 'en':
                output_translator = GoogleTranslator(source='en', target=target_lang_code)
                final_answer = output_translator.translate(text=found_answer_en)
            else:
                final_answer = found_answer_en

            return final_answer

        return None  # No answer found

    except Exception as e:
        # Provide a language-appropriate error message
        if st.session_state.language == 'العربية':
            return "عذراً، حدث خطأ في معالجة البيانات. يرجى مراجعة ملف CSV."
        else:
            return f"Data Processing Error: Could not process the request. ({str(e)})"


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
        placeholder="e.g., Who is the Grade 10 Social Worker?" if st.session_state.language == "English" else "مثل: من هي الأخصائية الاجتماعية للصف العاشر؟"
    )

    # Use a single button label for clarity
    submit_button = st.form_submit_button(label=f'{send_label}') 

if submit_button and user_input:
    # --- FIND ANSWER LOGIC ---
    answer = find_answer(user_input, school_data_df) # Call the function with the DataFrame

    # Handle case where no answer is found OR a data/translation error occurs
    if not answer or answer.startswith("عذراً، حدث خطأ") or answer.startswith("Data Processing Error"):
        if st.session_state.language == "English":
            answer = "I'm sorry, I couldn't find that specific information in the school data."
        else:
            answer = "عذراً، لم أجد هذه المعلومة المحددة في بيانات المدرسة."

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
