import streamlit as st
# You'll need the `openai` library installed for this code to work
# pip install openai

try:
    # 1. Access the secret directly using st.secrets
    # Streamlit automatically looks for a key named 'OPENAI_API_KEY'
    # in your secrets configuration.
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

    # 2. Add an optional check for a blank value
    if not OPENAI_API_KEY:
        st.error("Configuration Error: The 'OPENAI_API_KEY' secret is present but has no value. Please check your Streamlit Cloud secrets.")
        st.stop()
        
    # 3. Initialize the OpenAI Client
    # This is the most common way to use the key with the official OpenAI library
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY) 

except KeyError:
    # This block handles the case where the secret key is missing entirely
    st.error("FATAL ERROR: The secret key 'OPENAI_API_KEY' was not found.")
    st.markdown("Please ensure you have added it to your Streamlit Cloud secrets or to your local `.streamlit/secrets.toml` file.")
    st.stop()


# -------------------------------------------------------------
# You can now use the 'client' object throughout your Streamlit app
# -------------------------------------------------------------

st.title("My Secure Streamlit App")

# Example of how to call the OpenAI API
if st.button("Generate Response"):
    try:
        with st.spinner("Generating..."):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": "Write a short, fun fact about Python programming."}
                ]
            )
            st.success(response.choices[0].message.content)
            
    except Exception as e:
        st.error(f"An error occurred during API call: {e}")
