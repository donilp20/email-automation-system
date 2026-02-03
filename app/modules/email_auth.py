# app/modules/email_auth.py

import hashlib
from typing import Optional
import os

import streamlit as st

# Fix: Use absolute import or get from os.getenv directly
HASH_SALT = os.getenv("HASH_SALT", "change-me-in-env")


def hash_token(value: str) -> str:
    # optional: to avoid storing completely raw values
    data = (HASH_SALT + value).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def store_credentials(email: str, app_password: str) -> None:
    """
    Store in Streamlit session_state only.
    Never write to disk from inside container.
    """
    st.session_state["smtp_email"] = email
    st.session_state["smtp_app_password_hash"] = hash_token(app_password)
    st.session_state["smtp_app_password_plain"] = app_password  # in-memory only


def get_credentials() -> tuple[Optional[str], Optional[str]]:
    email = st.session_state.get("smtp_email")
    pwd = st.session_state.get("smtp_app_password_plain")
    return email, pwd
