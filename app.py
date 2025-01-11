import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from environment
api_key = os.getenv("API_KEY")
if not api_key:
    st.error("API key not found. Please set the API_KEY environment variable.")
    st.stop()

# Initialize OpenAI client without any additional configurations
try:
    client = OpenAI(api_key=api_key)
except Exception as e:
    st.error(f"Error initializing OpenAI client: {str(e)}")
    st.stop()

# Page config
st.set_page_config(page_title="My GPT Chat", page_icon="🤖")

# Title and description
st.title("Gulf Bank GPT")
st.markdown("---")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

# Chat interface
user_input = st.text_input("Your message:", value="")

if st.button("Send"):
    if user_input.strip():
        # Add user message
        st.session_state["messages"].append({"role": "user", "content": user_input})
        
        try:
            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state["messages"]
            )
            assistant_reply = response.choices[0].message.content
            st.session_state["messages"].append({"role": "assistant", "content": assistant_reply})
        except Exception as e:
            st.error(f"Error calling OpenAI API: {str(e)}")

# Display message history
for msg in st.session_state["messages"]:
    if msg["role"] != "system":
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        elif msg["role"] == "assistant":
            st.markdown(f"**Assistant:** {msg['content']}")