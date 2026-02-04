# app/modules/email_auth.py (UPDATED VERSION)

import hashlib
from typing import Optional, Tuple
import os

import streamlit as st
from .credential_storage import get_credential_storage


# Fix: Use absolute import or get from os.getenv directly
HASH_SALT = os.getenv("HASH_SALT", "change-me-in-env")


def hash_token(value: str) -> str:
    """Optional: to avoid storing completely raw values in memory."""
    data = (HASH_SALT + value).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def load_saved_credentials() -> None:
    """
    Load credentials from persistent storage into session state.
    Called once at app startup.
    """
    # Skip if already loaded in this session
    if "credentials_loaded" in st.session_state:
        return
    
    storage = get_credential_storage()
    email, app_password = storage.load_credentials()
    
    if email and app_password:
        # Store in session state
        st.session_state["smtp_email"] = email
        st.session_state["smtp_app_password_hash"] = hash_token(app_password)
        st.session_state["smtp_app_password_plain"] = app_password
        print(f"✅ Auto-loaded credentials for: {email}")
    
    # Mark as loaded (even if nothing was found)
    st.session_state["credentials_loaded"] = True


def store_credentials(email: str, app_password: str, persist: bool = True) -> None:
    """
    Store credentials in session state and optionally persist to disk.
    
    Args:
        email: Gmail address
        app_password: Gmail app password
        persist: If True, save to encrypted file on disk
    """
    # Store in session state (in-memory)
    st.session_state["smtp_email"] = email
    st.session_state["smtp_app_password_hash"] = hash_token(app_password)
    st.session_state["smtp_app_password_plain"] = app_password
    
    # Persist to disk if requested
    if persist:
        storage = get_credential_storage()
        storage.save_credentials(email, app_password)


def get_credentials() -> Tuple[Optional[str], Optional[str]]:
    """
    Get credentials from session state.
    
    Returns:
        Tuple of (email, app_password) or (None, None)
    """
    email = st.session_state.get("smtp_email")
    pwd = st.session_state.get("smtp_app_password_plain")
    return email, pwd


def clear_credentials(delete_from_disk: bool = True) -> None:
    """
    Clear credentials from session state and optionally from disk.
    
    Args:
        delete_from_disk: If True, also delete the encrypted file
    """
    # Clear from session state
    if "smtp_email" in st.session_state:
        del st.session_state["smtp_email"]
    if "smtp_app_password_plain" in st.session_state:
        del st.session_state["smtp_app_password_plain"]
    if "smtp_app_password_hash" in st.session_state:
        del st.session_state["smtp_app_password_hash"]
    
    # Clear from disk if requested
    if delete_from_disk:
        storage = get_credential_storage()
        storage.delete_credentials()


def credentials_are_saved_on_disk() -> bool:
    """Check if credentials exist in persistent storage."""
    storage = get_credential_storage()
    return storage.credentials_exist()
