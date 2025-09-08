import streamlit as st
import requests
import json
from typing import Dict, List
import os

API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

st.set_page_config(
    page_title="YouTube Video Q&A",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "video_processed" not in st.session_state:
    st.session_state.video_processed = False
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

def process_video(youtube_url: str) -> Dict:
    """Send video processing request to the API"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/process_video",
            json={"youtube_url": youtube_url},
            timeout=30
        )
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to backend: {str(e)}")
        return None
    
def ask_question(session_id: str, question: str) -> Dict:
    """Send question to the API and get the answer"""
    try:
        response = requests.post(
            f"{API_BASE_URL}/ask_question",
            json={"session_id": session_id, "question": question},
            timeout=30
        )
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to backend: {str(e)}")
        return None
    
def get_sessions() -> List[Dict]:
    """Fetch all active sessions from the API"""
    try:
        response = requests.get(f"{API_BASE_URL}/sessions", timeout=10)
        return response.json().get("sessions", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to backend: {str(e)}")
        return []
    
def delete_session(session_id: str):
    """Delete a session via the API"""
    try:
        response = requests.delete(f"{API_BASE_URL}/sessions/{session_id}", timeout=10)
        if response.status_code == 200:
            st.success("Session deleted successfully.")
            return True
        else:
            st.error(f"Failed to delete session: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        st.error(f"Error connecting to backend: {str(e)}")
        return False

# UI Layout code
st.title("YouTube Video Q&A App 🎥")

st.markdown("Ask questions about any YouTube video with transcripts!")

st.sidebar.header("📹 Process Video")

youtube_url = st.sidebar.text_input(
    "Enter YouTube URL:",
    placeholder="https://www.youtube.com/watch?v=...",
    help="Paste the YouTube video URL here"
)

# Process video button
if st.sidebar.button("Process Video"):
    if youtube_url:
        with st.sidebar:
            with st.spinner("Processing video... This may take a moment."):
                result = process_video(youtube_url=youtube_url)
                if result and "session_id" in result:
                    st.session_state.current_session_id = result["session_id"]
                    st.session_state.video_processed = True
                    st.session_state.chat_history = []
                    st.sidebar.success("✅ Video processed successfully!")
                    st.sidebar.info(f"Video ID: {result['video_id']}")
                else:
                    st.error("❌ Failed to process video. Please check the URL and try again.")
    else:
        st.sidebar.error("Please enter a valid YouTube URL.")

# Sidebar session management
st.sidebar.header("🗂️ Active Sessions")
sessions = get_sessions()

if sessions:
    st.sidebar.subheader("Active Sessions")
    for session in sessions:
        col1, col2 = st.sidebar.columns([3, 1])
        with col1:
            if st.button(f"📺 {session['video_id'][:8]}...", key=f"session_{session['session_id']}"):
                st.session_state.current_session_id = session['session_id']
                st.session_state.video_processed = True
                st.session_state.chat_history = []
        with col2:
            if st.button("🗑️", key=f"delete_{session['session_id']}", help="Delete session"):
                if delete_session(session['session_id']):
                    if st.session_state.current_session_id == session['session_id']:
                        st.session_state.current_session_id = None
                        st.session_state.video_processed = False
                        st.session_state.chat_history = []
                    st.rerun()

# Main content area
if not st.session_state.video_processed:
    st.info("Please process a YouTube video to start asking questions.")

    # Instructions
    st.markdown("""
    ### How to use:
    1. 📹 Paste a YouTube URL in the sidebar
    2. 🚀 Click "Process Video" to analyze the transcript
    3. 💬 Start asking questions about the video content
    
    ### Features:
    - 🎯 Ask specific questions about video content
    - 📝 Get answers based only on the video transcript
    - 💾 Multiple video sessions support
    - 🔄 Chat history for each session
    """)
else:
    # Chat Interface
    st.subheader("💬 Ask a Question about the Video")

    if st.session_state.current_session_id:
        st.info(f"Current Session ID: {st.session_state.current_session_id}")

    # Chat history display
    chat_container = st.container()

    with chat_container:
        for i, (question, answer) in enumerate(st.session_state.chat_history):
            # User question
            with st.chat_message("user", avatar="🧑"):
                st.write(question)
            # Bot answer
            with st.chat_message("assistant", avatar="🤖"):
                st.write(answer)

    # Question input
    question = st.chat_input("Type your question about the video...")

    if question:
        # Add user question to chat
        with st.chat_message("user", avatar="🧑"):
            st.write(question)

        # Get answer from backend
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("Thinking..."):
                response = ask_question(st.session_state.current_session_id, question)
                if response and "answer" in response:
                    answer = response["answer"]
                    st.write(answer)
                    # Save to chat history
                    st.session_state.chat_history.append((question, answer))
                else:
                    st.error("❌ Failed to get an answer. Please try again.")

# Clear chat button
if st.session_state.video_processed and st.session_state.chat_history:
    if st.button("Clear Chat History"):
        st.session_state.chat_history = []
        st.rerun()

# Footer
st.markdown("---")
st.markdown("Developed with ❤️ By Swapneil Basutkar")