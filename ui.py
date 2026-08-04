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
/* Dynamic Animated Gradient Background */
@keyframes gradientBG {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.stApp {
    background: linear-gradient(-45deg, #0a0510, #1a0b2e, #0d122a, #1f0b18);
    background-size: 400% 400%;
    animation: gradientBG 15s ease infinite;
    color: #ffffff;
}

/* Glassmorphism Chat Messages */
.stChatMessage {
    background: rgba(255, 255, 255, 0.03) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255, 255, 255, 0.07) !important;
    border-radius: 20px !important;
    padding: 1.5rem !important;
    margin-bottom: 1.5rem !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4) !important;
    transition: all 0.3s ease !important;
}

.stChatMessage:hover {
    transform: translateY(-2px);
    border-color: rgba(255, 75, 145, 0.4) !important;
    box-shadow: 0 12px 40px 0 rgba(255, 75, 145, 0.15) !important;
}

/* Chat Avatars */
[data-testid="chatAvatarIcon-user"] {
    background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%) !important;
    color: white !important;
}

[data-testid="chatAvatarIcon-assistant"] {
    background: linear-gradient(135deg, #ff0844 0%, #ffb199 100%) !important;
    color: white !important;
}

/* Text Input Container */
[data-testid="stChatInput"] {
    background: rgba(10, 5, 20, 0.6) !important;
    backdrop-filter: blur(20px) !important;
    border: 1px solid rgba(255, 255, 255, 0.15) !important;
    border-radius: 30px !important;
    box-shadow: 0 0 20px rgba(0,242,254,0.1) !important;
    transition: border-color 0.3s ease !important;
}

[data-testid="stChatInput"]:focus-within {
    border-color: #00f2fe !important;
    box-shadow: 0 0 30px rgba(0,242,254,0.3) !important;
}

/* Header Text */
h1 {
    background: -webkit-linear-gradient(45deg, #ff0844, #ffb199, #00f2fe);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-shadow: 0px 0px 30px rgba(255, 8, 68, 0.3);
    font-weight: 900 !important;
    text-align: center;
    letter-spacing: -1px;
    margin-bottom: 2rem !important;
}

/* Alert Styling */
.stAlert {
    background: rgba(255, 171, 0, 0.1) !important;
    border-left: 4px solid #ffab00 !important;
    color: #ffab00 !important;
    backdrop-filter: blur(10px);
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
