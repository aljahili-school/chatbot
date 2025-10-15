import streamlit as st
import os

# ----------------------------------------------------------------------
# Section 1: Security and API Key (All commented out to disable AI)
# ----------------------------------------------------------------------

# The following code blocks are commented out. This ensures your app runs 
# without needing the 'openai' library, the 'OPENAI_API_KEY' secret, 
# or an active OpenAI billing account.

# try:
#     # Attempt to access the secret key (will be skipped)
#     OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
#     from openai import OpenAI
#     client = OpenAI(api_key=OPENAI_API_KEY)
# except Exception:
#     # Pass the error so the app continues to run without AI
#     pass


# ----------------------------------------------------------------------
# Section 2: Streamlit Application Interface
# ----------------------------------------------------------------------

st.title("My School Project (AI Feature Disabled)")
st.caption("The application is running in non-AI mode to avoid the quota error.")

st.header("Static File Data")
st.write("Below are the documents available for the project:")

# Display the files you previously mentioned/uploaded
st.markdown("* school_data.pdf")
st.markdown("* school_data.xlsx")
st.markdown("* requirements.txt")

st.write("---")

# ----------------------------------------------------------------------
# Section 3: Replacement for AI Logic
# ----------------------------------------------------------------------

user_input = st.text_input("Ask a question about the school data:", 
                           value="What are the main requirements of this project?")

if st.button("Get Answer"):
    # This block provides a static, non-AI response instead of calling OpenAI
    if user_input:
        st.info("The AI capability is currently **disabled**.")
        st.warning("To get an answer based on your documents, you need to fix the 'insufficient_quota' error on your OpenAI account and re-enable the AI code.")
        
        # Display a sample static response
        st.code("""
        # Example of what the AI would do:
        # 1. Load documents (PDF, Excel)
        # 2. Search for relevant text
        # 3. Use GPT-3.5 to generate an answer
        
        # Static Response:
        'The main requirements of the project are documented in the `requirements.txt` file 
        and the specific data details are in `school_data.xlsx`.'
        """)
    else:
        st.error("Please enter a question.")

# ----------------------------------------------------------------------
