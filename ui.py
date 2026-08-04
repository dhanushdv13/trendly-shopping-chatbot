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
/* Exact ChatGPT Clone Theme */
.stApp {
    background-color: #000000 !important;
    color: #ececec !important;
}

header {
    visibility: hidden;
}

/* Chat Messages */
.stChatMessage {
    background: transparent !important;
    border: none !important;
    padding: 1.5rem 0 !important;
    margin: 0 !important;
    box-shadow: none !important;
    border-bottom: none !important;
    color: #ececec !important;
}

.stChatMessage p, .stChatMessage div, .stChatMessage span {
    color: #ececec !important;
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
    background: transparent !important; 
    border: 1px solid #444 !important; 
    color: #ececec !important;
}

/* User Avatar */
[data-testid="chatAvatarIcon-user"] {
    background: #333333 !important; 
    border: none !important; 
    color: #ececec !important;
}

/* Chat Input Container */
[data-testid="stChatInput"] {
    background-color: #2f2f2f !important;
    border: none !important;
    border-radius: 30px !important;
    padding: 0.5rem 1rem !important;
    box-shadow: none !important;
    transition: none !important;
}

[data-testid="stChatInput"]:focus-within {
    border: none !important;
    box-shadow: none !important;
}

/* Ensure text inside the input box is readable */
.stChatInputContainer textarea {
    color: #ececec !important; 
    font-size: 1rem !important;
}

.stChatInputContainer textarea::placeholder {
    color: #8e8ea0 !important; 
}

/* Header Text */
h1 {
    color: #ececec !important;
    font-weight: 400 !important;
    text-align: center;
    font-size: 2rem !important;
    margin-bottom: 2rem !important;
    background: none !important;
    -webkit-text-fill-color: initial !important;
    text-shadow: none !important;
}

/* Alert Styling */
.stAlert {
    background-color: #2f2f2f !important; 
    border: none !important; 
    color: #ececec !important;
    border-radius: 8px !important;
}

/* Hide Streamlit Branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Top Left Logo Injection
st.markdown("<div style='position: fixed; top: 15px; left: 20px; z-index: 9999; color: #ececec; font-size: 1.1rem; font-weight: 600; font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, sans-serif; display: flex; align-items: center; gap: 5px; cursor: pointer;'>Trendly <span style='font-size: 0.8rem; color: #8e8ea0; margin-top: 2px;'>⌄</span></div>", unsafe_allow_html=True)

# Centered Greeting
st.markdown("<h1 style='text-align: center; font-weight: normal; margin-top: 10vh;'>Ready when you are.</h1>", unsafe_allow_html=True)

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
if prompt := st.chat_input("Ask anything"):
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
