# app/config.py

import os

# Ollama / LLM
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")

# Email (we'll use app password or OAuth token instead of raw password)
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))

# Security
HASH_SALT = os.getenv("HASH_SALT", "change-me-in-env")

# Streamlit
APP_TITLE = "Email Automation System"