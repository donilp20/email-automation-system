import streamlit as st
from typing import Dict, Any
from .supabase_client import get_supabase_client


DEFAULT_PREFERENCES = {
    "email_tone": "formal",
    "sender_name": "",
    "cc_emails": "",
    "bcc_emails": "",
    "subject_prefix": "",
    "default_recipient": "",
    "default_subject": "",
}


def save_preferences(user_id: str, preferences: Dict[str, Any]) -> bool:
    """
    Save user preferences to Supabase.
    
    Args:
        user_id: Unique identifier for the user
        preferences: Dictionary of user preferences
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        supabase = get_supabase_client()
        
        # Check if user exists
        response = supabase.table("user_config").select("*").eq("user_id", user_id).execute()
        
        if response.data:
            # Update preferences
            supabase.table("user_config").update({
                "preferences": preferences
            }).eq("user_id", user_id).execute()
            print(f"Updated preferences for: {user_id}")
        else:
            # Create new entry if user doesn't exist
            supabase.table("user_config").insert({
                "user_id": user_id,
                "email_address": "",
                "encrypted_app_password": "",
                "preferences": preferences
            }).execute()
            print(f"Created preferences for: {user_id}")
        
        return True
    except Exception as e:
        st.error(f"Failed to save preferences: {e}")
        print(f"Failed to save preferences: {e}")
        return False


def load_preferences(user_id: str) -> Dict[str, Any]:
    """
    Load user preferences from Supabase.
    
    Args:
        user_id: Unique identifier for the user
    
    Returns:
        Dict of preferences, or default preferences if not found
    """
    try:
        supabase = get_supabase_client()
        response = supabase.table("user_config").select("preferences").eq("user_id", user_id).execute()
        
        if response.data and response.data[0].get("preferences"):
            # Merge with defaults to ensure all keys exist
            saved_prefs = response.data[0]["preferences"]
            return {**DEFAULT_PREFERENCES, **saved_prefs}
        
        print(f"No preferences found for: {user_id}, using defaults")
        return DEFAULT_PREFERENCES.copy()
    except Exception as e:
        st.error(f"Failed to load preferences: {e}")
        print(f"Failed to load preferences: {e}")
        return DEFAULT_PREFERENCES.copy()


def clear_preferences(user_id: str) -> bool:
    """Reset user preferences to defaults."""
    return save_preferences(user_id, DEFAULT_PREFERENCES.copy())


def get_preference(user_id: str, key: str, default: Any = None) -> Any:
    """Get a specific preference value."""
    prefs = load_preferences(user_id)
    return prefs.get(key, default)


def preferences_exist(user_id: str) -> bool:
    """Check if preferences exist for a user."""
    try:
        supabase = get_supabase_client()
        response = supabase.table("user_config").select("preferences").eq("user_id", user_id).execute()
        return len(response.data) > 0 and response.data[0].get("preferences") is not None
    except Exception as e:
        print(f"Failed to check preferences: {e}")
        return False
