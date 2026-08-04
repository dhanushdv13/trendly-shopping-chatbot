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
/* ChatGPT Minimalist Dark Theme */
.stApp {
    background-color: #212121;
    color: #ececec;
}

/* Chat Messages - Flat and Minimal */
.stChatMessage {
    background: transparent !important;
    border: none !important;
    border-radius: 0 !important;
    padding: 1.5rem 0 !important;
    margin: 0 !important;
    box-shadow: none !important;
}

/* Assistant message specific background if desired */
[data-testid="stChatMessage"]:nth-child(even) {
    background-color: #212121 !important;
}
[data-testid="stChatMessage"]:nth-child(odd) {
    background-color: #212121 !important;
}

/* Assistant Avatar */
[data-testid="chatAvatarIcon-assistant"] {
    background-color: #10a37f !important;
    color: white !important;
}

/* User Avatar */
[data-testid="chatAvatarIcon-user"] {
    background-color: #5436da !important;
    color: white !important;
}

/* Chat Input Container */
[data-testid="stChatInput"] {
    background-color: #2f2f2f !important;
    border: 1px solid #424242 !important;
    border-radius: 12px !important;
    padding: 0.2rem !important;
    box-shadow: none !important;
    transition: none !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: #565656 !important;
    box-shadow: none !important;
}

/* Header Text */
h1 {
    color: #ececec !important;
    font-weight: 600 !important;
    text-align: center;
    font-size: 1.8rem !important;
    margin-bottom: 2rem !important;
    background: none !important;
    -webkit-text-fill-color: initial !important;
    text-shadow: none !important;
}

/* Alert Styling */
.stAlert {
    background-color: #2f2f2f !important;
    border: 1px solid #424242 !important;
    color: #ececec !important;
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
