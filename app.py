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

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Custom CSS for the chat interface
st.markdown("""
    <style>
        /* Hide Streamlit's default footer */
        footer {display: none}
        
        /* Container styling */
        .stApp {
            background-color: white;
        }
        
        /* Chat message container */
        .chat-message {
            padding: 1rem 1.5rem;
            margin: 0.5rem 0;
            border-radius: 0.5rem;
        }
        
        /* User message styling */
        .user-message {
            background-color: #f7f7f8;
        }
        
        /* Assistant message styling */
        .assistant-message {
            background-color: white;
            border-top: 1px solid #e5e5e5;
            border-bottom: 1px solid #e5e5e5;
        }
        
        /* Input container styling */
        .stTextInput {
            position: fixed;
            bottom: 0;
            background-color: white;
            padding: 1rem 0;
            left: 0;
            right: 0;
            z-index: 100;
            border-top: 1px solid #e5e5e5;
        }
        
        /* Add padding at the bottom to prevent content from being hidden behind input */
        .main-container {
            padding-bottom: 5rem;
        }
    </style>
""", unsafe_allow_html=True)

# Page config
st.set_page_config(page_title="My GPT Chat", page_icon="🤖")

# Display logo
try:
    st.image("assets/images/gbk_logo.svg", width=150)
except Exception as e:
    st.error(f"Error loading image: {str(e)}")

st.title("Gulf Bank GPT")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

# Create a container for the chat messages
with st.container():
    st.markdown('<div class="main-container">', unsafe_allow_html=True)
    
    # Display chat messages
    for msg in st.session_state["messages"]:
        if msg["role"] != "system":
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {msg["content"]}</div>', 
                          unsafe_allow_html=True)
            elif msg["role"] == "assistant":
                st.markdown(f'<div class="chat-message assistant-message"><strong>Assistant:</strong> {msg["content"]}</div>', 
                          unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Create the input box at the bottom
with st.container():
    user_input = st.text_input("Your message:", key="user_input", value="")
    
    # Handle the input
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
            
            # Clear the input
            st.session_state["user_input"] = ""
            
            # Rerun to update the chat
            st.rerun()
            
        except Exception as e:
            st.error(f"Error calling OpenAI API: {str(e)}")