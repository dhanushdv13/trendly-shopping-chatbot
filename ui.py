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
/* Single Royal Color Theme */
.stApp {
    background-color: #0b1a38 !important; /* Little dark royal blue */
    color: #ffffff !important; /* Light text on dark background */
}

/* Chat Messages */
.stChatMessage {
    background: transparent !important;
    border: none !important;
    padding: 1.5rem 0 !important;
    margin: 0 !important;
    box-shadow: none !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
}

/* Assistant message specific background */
[data-testid="stChatMessage"]:nth-child(even) {
    background-color: transparent !important;
}
[data-testid="stChatMessage"]:nth-child(odd) {
    background-color: transparent !important;
}

/* Assistant Avatar */
[data-testid="chatAvatarIcon-assistant"] {
    background: #1c3d7a !important; /* Royal blue accent */
    border: 1px solid #2e59a8 !important;
    color: #ffffff !important;
}

/* User Avatar */
[data-testid="chatAvatarIcon-user"] {
    background: #2e59a8 !important; /* Lighter royal accent */
    border: 1px solid #4a7fdc !important;
    color: #ffffff !important;
}

/* Chat Input Container - Light Color */
[data-testid="stChatInput"] {
    background-color: #f8f9fa !important; /* Light color */
    border: 1px solid #dee2e6 !important;
    border-radius: 12px !important;
    padding: 0.5rem !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2) !important;
    transition: all 0.3s ease !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: #1c3d7a !important;
    box-shadow: 0 0 10px rgba(28, 61, 122, 0.3) !important;
}

/* Ensure text inside the light input box is dark and readable */
.stChatInputContainer textarea {
    color: #000000 !important; 
}

.stChatInputContainer textarea::placeholder {
    color: #6c757d !important;
}

/* Header Text */
h1 {
    color: #ffffff !important;
    font-weight: 500 !important;
    text-align: center;
    font-size: 2.2rem !important;
    margin-bottom: 2rem !important;
    background: none !important;
    -webkit-text-fill-color: initial !important;
    text-shadow: none !important;
}

/* Alert Styling */
.stAlert {
    background-color: #1c3d7a !important;
    border: 1px solid #ff4444 !important;
    color: #ffffff !important;
    border-radius: 8px !important;
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
