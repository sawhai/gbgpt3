#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 12 22:41:41 2025

@author: ha
"""
import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
from PyPDF2 import PdfReader
import docx
import pandas as pd

# Load environment variables
load_dotenv()

# Get API key from environment
api_key = os.getenv("API_KEY")
if not api_key:
    st.error("API key not found. Please set the API_KEY environment variable.")
    st.stop()

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Page config
st.set_page_config(page_title="My GPT Chat", page_icon="🤖")

# Display logo - using relative path
try:
    st.image("assets/images/gbk_logo.svg", width=150)
except Exception as e:
    st.error(f"Error loading image: {str(e)}")

st.title("Gulf Bank GPT")
st.markdown("---")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "assistant", "content": "I am your AI assistant at Gulf Bank, how can I help you today?"}
    ]
    st.session_state["file_context"] = None  # Store file content here
    st.session_state["user_input"] = ""  # Store user input

# Function to extract text from uploaded file
def extract_text(file):
    if file.name.endswith(".pdf"):
        pdf_reader = PdfReader(file)
        return "\n".join(page.extract_text() for page in pdf_reader.pages)
    elif file.name.endswith(".docx"):
        doc = docx.Document(file)
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)
    elif file.name.endswith(".txt"):
        return file.read().decode("utf-8")
    elif file.name.endswith((".xls", ".xlsx")):
        df = pd.read_excel(file)
        return df.to_string(index=False)  # Convert the DataFrame to a string
    else:
        st.error("Unsupported file format. Please upload a PDF, DOCX, TXT, or Excel file.")
        return None

# Function to handle sending messages
def send_message():
    user_input = st.session_state["user_input"]
    if user_input.strip():
        # Add user message
        st.session_state["messages"].append({"role": "user", "content": user_input})
        st.session_state["user_input"] = ""  # Clear input box

        # Prepare context for the OpenAI API
        context = st.session_state["file_context"] if st.session_state.get("file_context") else ""
        messages = st.session_state["messages"].copy()
        if context:
            messages.append({"role": "system", "content": f"Context from uploaded file: {context}"})

        try:
            # Call OpenAI API
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )
            assistant_reply = response.choices[0].message.content
            st.session_state["messages"].append({"role": "assistant", "content": assistant_reply})
        except Exception as e:
            st.error(f"Error calling OpenAI API: {str(e)}")

# Reverse chat interface layout
with st.container():
    # Display message history in reverse order
    chat_placeholder = st.empty()  # Placeholder for chat history
    chat_history = [
        f"**You:** {msg['content']}" if msg["role"] == "user" else f"**Assistant:** {msg['content']}"
        for msg in st.session_state["messages"]
        if msg["role"] != "system"
    ]
    chat_placeholder.markdown("\n\n".join(reversed(chat_history)))

    # File upload at the bottom
    uploaded_file = st.file_uploader("Upload a document (PDF, DOCX, TXT, or Excel):", type=["pdf", "docx", "txt", "xls", "xlsx"])
    if uploaded_file:
        file_content = extract_text(uploaded_file)
        if file_content:
            st.session_state["file_context"] = file_content
            st.success("File uploaded successfully. You can now ask questions about its content.")

    # Chat input below file uploader
    st.text_input("Your message:", value=st.session_state["user_input"], on_change=send_message, key="user_input")
