import hashlib
import smtplib
from typing import Optional, Tuple
import os

import streamlit as st
from .credential_storage import get_credential_storage

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
    
    # ADD THIS - Invalidate cache when saving
    if "_credentials_disk_check_cache" in st.session_state:
        del st.session_state["_credentials_disk_check_cache"]
    
    # Persist to disk if requested
    if persist:
        storage = get_credential_storage()
        success = storage.save_credentials(email, app_password)
        if success:
            print(f"✅ Credentials stored and persisted for: {email}")


def get_credentials() -> Tuple[Optional[str], Optional[str]]:
    """
    Get credentials from session state.
    
    Returns:
        Tuple of (email, app_password) or (None, None)
    """
    email = st.session_state.get("smtp_email")
    pwd = st.session_state.get("smtp_app_password_plain")

    # ADD THIS DEBUG LOGGING
    if email and pwd:
        print(f"✅ get_credentials() - Email: {email}, Password: {'*' * len(pwd)} ({len(pwd)} chars)")
    elif email and not pwd:
        print(f"⚠️  get_credentials() - Email found but password is None!")
    else:
        print(f"❌ get_credentials() - No credentials in session state")

    return email, pwd


def clear_credentials(delete_from_disk: bool = True) -> None:
    """
    Clear credentials from session state and optionally from disk.
    
    Args:
        delete_from_disk: If True, also delete the encrypted file
    """
    # Clear from session state
    keys_to_clear = [
        "smtp_email",
        "smtp_app_password_plain",
        "smtp_app_password_hash",
        "credentials_loaded",
        "_credentials_disk_check_cache"  # ADD THIS
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            del st.session_state[key]
    
    # Clear from disk if requested
    if delete_from_disk:
        storage = get_credential_storage()
        storage.delete_credentials()
        print("✅ Credentials cleared from session and disk")


def credentials_are_saved_on_disk() -> bool:
    """
    Check if credentials exist in persistent storage.
    Cached to avoid excessive file system checks.
    """
    # USE CACHED RESULT TO PREVENT INFINITE LOOP
    cache_key = "_credentials_disk_check_cache"
    
    # Return cached value if exists
    if cache_key in st.session_state:
        return st.session_state[cache_key]
    
    # Check file system
    storage = get_credential_storage()
    exists = storage.credentials_exist()
    
    # Cache the result
    st.session_state[cache_key] = exists
    
    return exists


def validate_credentials(email: str, app_password: str) -> Tuple[bool, str]:
    """
    Test Gmail credentials by attempting to authenticate with SMTP server.
    
    Args:
        email: Gmail address
        app_password: Gmail app password
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    
    try:
        # Attempt to connect and authenticate
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=10)
        server.starttls()
        server.login(email, app_password)
        server.quit()
        
        return (True, "")
        
    except smtplib.SMTPAuthenticationError as e:
        # Invalid credentials
        error_msg = str(e)
        
        if "535" in error_msg or "Username and Password not accepted" in error_msg:
            return (False, "Invalid credentials. Please use an App Password (not regular password)\n")
        else:
            return (False, f"Authentication failed: {error_msg}")
    
    except smtplib.SMTPException as e:
        # Other SMTP errors
        return (False, f"SMTP error: {str(e)}")
    
    except ConnectionError as e:
        # Network issues
        return (False, f"Connection error: {str(e)}")
    
    except TimeoutError:
        # Timeout
        return (False, "Connection timeout. Please check your internet connection.")
    
    except Exception as e:
        # Catch-all for unexpected errors
        return (False, f"Unexpected error: {str(e)}")