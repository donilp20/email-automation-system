"""Secure credential storage using Supabase PostgreSQL."""
from cryptography.fernet import Fernet
import streamlit as st
from typing import Optional, Dict
from .supabase_client import get_supabase_client


def get_encryption_key() -> bytes:
    """Get encryption key from secrets or generate one for development."""
    if "ENCRYPTION_KEY" in st.secrets:
        return st.secrets["ENCRYPTION_KEY"].encode()
    else:
        # For development only - in production, always use secrets
        st.warning("⚠️ Using temporary encryption key. Set ENCRYPTION_KEY in secrets for production.")
        return Fernet.generate_key()


def encrypt_password(password: str) -> str:
    """Encrypt the app password."""
    fernet = Fernet(get_encryption_key())
    return fernet.encrypt(password.encode()).decode()


def decrypt_password(encrypted_password: str) -> str:
    """Decrypt the app password."""
    fernet = Fernet(get_encryption_key())
    return fernet.decrypt(encrypted_password.encode()).decode()


def save_credentials(user_id: str, email: str, app_password: str) -> bool:
    """
    Save user credentials to Supabase.
    
    Args:
        user_id: Unique identifier for the user (typically the email itself)
        email: User's email address
        app_password: Gmail app password (will be encrypted)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        supabase = get_supabase_client()
        encrypted_pwd = encrypt_password(app_password)
        
        # Check if user exists
        response = supabase.table("user_config").select("*").eq("user_id", user_id).execute()
        
        if response.data:
            # Update existing user
            supabase.table("user_config").update({
                "email_address": email,
                "encrypted_app_password": encrypted_pwd
            }).eq("user_id", user_id).execute()
            print(f"✅ Updated credentials for: {user_id}")
        else:
            # Insert new user
            supabase.table("user_config").insert({
                "user_id": user_id,
                "email_address": email,
                "encrypted_app_password": encrypted_pwd,
                "preferences": {}
            }).execute()
            print(f"✅ Created new credentials for: {user_id}")
        
        return True
    except Exception as e:
        st.error(f"Failed to save credentials: {e}")
        print(f"❌ Failed to save credentials: {e}")
        return False


def load_credentials(user_id: str) -> Optional[Dict[str, str]]:
    """
    Load user credentials from Supabase.
    
    Args:
        user_id: Unique identifier for the user
    
    Returns:
        Dict with 'email' and 'app_password' keys, or None if not found
    """
    try:
        supabase = get_supabase_client()
        response = supabase.table("user_config").select("*").eq("user_id", user_id).execute()
        
        if response.data:
            data = response.data[0]
            return {
                "email": data["email_address"],
                "app_password": decrypt_password(data["encrypted_app_password"])
            }
        print(f"ℹ️ No credentials found for: {user_id}")
        return None
    except Exception as e:
        st.error(f"Failed to load credentials: {e}")
        print(f"❌ Failed to load credentials: {e}")
        return None


def delete_credentials(user_id: str) -> bool:
    """Delete user credentials from Supabase."""
    try:
        supabase = get_supabase_client()
        supabase.table("user_config").delete().eq("user_id", user_id).execute()
        print(f"✅ Deleted credentials for: {user_id}")
        return True
    except Exception as e:
        st.error(f"Failed to delete credentials: {e}")
        print(f"❌ Failed to delete credentials: {e}")
        return False


def credentials_exist(user_id: str) -> bool:
    """Check if credentials exist for a user."""
    try:
        supabase = get_supabase_client()
        response = supabase.table("user_config").select("id").eq("user_id", user_id).execute()
        return len(response.data) > 0
    except Exception as e:
        print(f"❌ Failed to check credentials: {e}")
        return False


# Legacy compatibility functions (for backward compatibility with existing code)
class CredentialStorage:
    """Legacy wrapper for backward compatibility."""
    
    def __init__(self, storage_dir: str = None):
        # Ignore storage_dir in cloud mode
        self.user_id = None
        print("📁 Using Supabase for credential storage (cloud mode)")
    
    def save_credentials(self, email: str, app_password: str) -> bool:
        # Use email as user_id
        return save_credentials(email, email, app_password)
    
    def load_credentials(self):
        # This requires user_id to be set first
        if not self.user_id:
            return None, None
        
        result = load_credentials(self.user_id)
        if result:
            return result["email"], result["app_password"]
        return None, None
    
    def delete_credentials(self) -> bool:
        if not self.user_id:
            return False
        return delete_credentials(self.user_id)
    
    def credentials_exist(self) -> bool:
        if not self.user_id:
            return False
        return credentials_exist(self.user_id)


_storage_instance = None


def get_credential_storage() -> CredentialStorage:
    """Get or create singleton credential storage instance (legacy)."""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = CredentialStorage()
    return _storage_instance
