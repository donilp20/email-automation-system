# app/modules/credential_storage.py

import os
import json
from pathlib import Path
from typing import Optional, Tuple
from cryptography.fernet import Fernet
import base64
import hashlib


class CredentialStorage:
    """
    Handles secure local storage of Gmail credentials.
    Uses Fernet symmetric encryption with a key derived from machine-specific data.
    """
    
    def __init__(self, storage_dir: str = "app/data"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.credentials_file = self.storage_dir / ".credentials.enc"
        self.cipher = self._get_cipher()
    
    def _generate_machine_key(self) -> bytes:
        """
        Generate a machine-specific encryption key.
        This uses a combination of hostname and a fixed salt.
        
        Note: This is not ultra-secure but good enough for local storage.
        For production, consider using keyring or proper secret management.
        """
        import socket
        
        # Use hostname + fixed salt for deterministic key
        hostname = socket.gethostname()
        salt = "email-automation-v1-salt"  # Change this to something unique
        
        # Derive key from hostname + salt
        key_material = f"{hostname}:{salt}".encode()
        key_hash = hashlib.sha256(key_material).digest()
        
        # Fernet requires base64-encoded 32-byte key
        return base64.urlsafe_b64encode(key_hash)
    
    def _get_cipher(self) -> Fernet:
        """Get or create encryption cipher."""
        key = self._generate_machine_key()
        return Fernet(key)
    
    def save_credentials(self, email: str, app_password: str) -> bool:
        """
        Save credentials to encrypted file.
        
        Args:
            email: Gmail address
            app_password: Gmail app password
            
        Returns:
            True if saved successfully
        """
        try:
            # Create credentials dictionary
            credentials = {
                "email": email,
                "app_password": app_password
            }
            
            # Serialize to JSON
            json_data = json.dumps(credentials)
            
            # Encrypt
            encrypted_data = self.cipher.encrypt(json_data.encode())
            
            # Write to file
            self.credentials_file.write_bytes(encrypted_data)
            
            print(f"✅ Credentials saved to {self.credentials_file}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to save credentials: {e}")
            return False
    
    def load_credentials(self) -> Tuple[Optional[str], Optional[str]]:
        """
        Load credentials from encrypted file.
        
        Returns:
            Tuple of (email, app_password) or (None, None) if not found
        """
        try:
            # Check if file exists
            if not self.credentials_file.exists():
                print("ℹ️  No saved credentials found")
                return None, None
            
            # Read encrypted data
            encrypted_data = self.credentials_file.read_bytes()
            
            # Decrypt
            decrypted_data = self.cipher.decrypt(encrypted_data)
            
            # Parse JSON
            credentials = json.loads(decrypted_data.decode())
            
            email = credentials.get("email")
            app_password = credentials.get("app_password")
            
            if email and app_password:
                print(f"✅ Loaded credentials for: {email}")
                return email, app_password
            else:
                print("⚠️  Credentials file is incomplete")
                return None, None
                
        except Exception as e:
            print(f"❌ Failed to load credentials: {e}")
            return None, None
    
    def delete_credentials(self) -> bool:
        """
        Delete stored credentials.
        
        Returns:
            True if deleted successfully
        """
        try:
            if self.credentials_file.exists():
                self.credentials_file.unlink()
                print("✅ Credentials deleted")
                return True
            else:
                print("ℹ️  No credentials to delete")
                return True
                
        except Exception as e:
            print(f"❌ Failed to delete credentials: {e}")
            return False
    
    def credentials_exist(self) -> bool:
        """Check if credentials file exists."""
        return self.credentials_file.exists()


# Singleton instance
_storage_instance = None


def get_credential_storage() -> CredentialStorage:
    """Get or create singleton credential storage instance."""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = CredentialStorage()
    return _storage_instance
