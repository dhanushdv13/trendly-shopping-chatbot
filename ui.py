import streamlit as st
import requests
import uuid
import os

# Configuration
API_URL = os.environ.get("API_URL", "http://127.0.0.1:8000/chat")
if not API_URL.endswith("/chat"):
    API_URL = f"{API_URL.rstrip('/')}/chat"

st.set_page_config(page_title="Trendly Support", page_icon="✨", layout="wide")

# Unique Dynamic CSS Injection
CUSTOM_CSS = """
<style>
/* Full Dark Surreal Theme */
.stApp {
    background-color: #000000 !important;
    color: #e0e0e0 !important;
}

/* Chat Messages */
.stChatMessage {
    background: transparent !important;
    border: none !important;
    padding: 2rem 0 !important;
    margin: 0 !important;
    box-shadow: none !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
}

/* Assistant message specific background if desired */
[data-testid="stChatMessage"]:nth-child(even) {
    background-color: transparent !important;
}
[data-testid="stChatMessage"]:nth-child(odd) {
    background-color: transparent !important;
}

/* Assistant Avatar */
[data-testid="chatAvatarIcon-assistant"] {
    background: #000000 !important;
    border: 1px solid rgba(255, 255, 255, 0.3) !important;
    color: #ffffff !important;
    box-shadow: 0 0 15px rgba(255, 255, 255, 0.1) !important;
}

/* User Avatar */
[data-testid="chatAvatarIcon-user"] {
    background: #000000 !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    color: #888888 !important;
}

/* Chat Input Container */
[data-testid="stChatInput"] {
    background-color: #050505 !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 0 !important;
    padding: 0.5rem !important;
    box-shadow: 0 0 20px rgba(0, 0, 0, 0.8) !important;
    transition: all 0.5s ease !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: rgba(255, 255, 255, 0.5) !important;
    box-shadow: 0 0 30px rgba(255, 255, 255, 0.05) !important;
}

.stChatInputContainer textarea {
    color: #ffffff !important;
}

/* Header Text */
h1 {
    color: #ffffff !important;
    font-weight: 300 !important;
    text-align: center;
    font-size: 2rem !important;
    letter-spacing: 4px;
    margin-bottom: 3rem !important;
    text-transform: uppercase;
    background: none !important;
    -webkit-text-fill-color: initial !important;
    text-shadow: 0 0 10px rgba(255, 255, 255, 0.2) !important;
}

/* Alert Styling */
.stAlert {
    background-color: #000000 !important;
    border: 1px solid rgba(255, 0, 0, 0.3) !important;
    color: #ff4444 !important;
    border-radius: 0 !important;
}

/* Hide Streamlit Branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
st.title("Trendly AI ✨")

# Initialize session state for messages and session_id
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi! I'm the Trendly Support Agent. How can I help you today?"}
    ]

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input
if prompt := st.chat_input("Ask me about orders, returns, or policies..."):
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
        
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Get bot response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response = requests.post(
                    API_URL,
                    json={"session_id": st.session_state.session_id, "message": prompt}
                )
                response.raise_for_status()
                data = response.json()
                
                reply = data.get("reply", "Sorry, I received an empty response.")
                st.markdown(reply)
                
                st.session_state.messages.append({"role": "assistant", "content": reply})
                
                if data.get("escalated"):
                    st.warning("⚠️ This conversation has been escalated to a human agent.")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to the support server: {e}")
                st.info("Make sure the FastAPI backend is running on http://127.0.0.1:8000")
