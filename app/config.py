"""Application configuration for cloud deployment."""
import streamlit as st


# Application metadata
APP_TITLE = "Email Automation System"
APP_VERSION = "2.0.0-cloud"

# Model configuration (using Groq)
DEFAULT_MODEL = "llama-3.1-8b-instant"

# Email configuration (cloud-compatible)
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465  # SSL port for cloud compatibility

# Session state keys
SESSION_KEYS = {
    "user_id": "current_user_id",
    "authenticated": "is_authenticated",
    "credentials": "user_credentials",
    "preferences": "user_preferences",
    "generated_email": "current_email"
}


def init_session_state():
    """Initialize Streamlit session state with default values."""
    for key, session_key in SESSION_KEYS.items():
        if session_key not in st.session_state:
            st.session_state[session_key] = None
