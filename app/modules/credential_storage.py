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
    
    def __init__(self, storage_dir: str = None):
        # Determine storage directory
        if storage_dir is None:
            # Try to use app/data relative to the current working directory
            storage_dir = os.path.join(os.getcwd(), "app", "data")
        
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.credentials_file = self.storage_dir / ".credentials.enc"
        
        print(f"📁 Credential storage path: {self.credentials_file}")
        
        self.cipher = self._get_cipher()
    
    def _generate_machine_key(self) -> bytes:
        """
        Generate a machine-specific encryption key.
        This uses a fixed salt for deterministic key generation.
        
        Note: For production, consider using keyring or proper secret management.
        """
        # Use a fixed salt instead of hostname to ensure consistency
        # even when container hostname changes
        salt = "email-automation-v1-deterministic-key"
        
        # Derive key from salt
        key_material = salt.encode()
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
            import traceback
            traceback.print_exc()
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
                print(f"ℹ️  No saved credentials found at {self.credentials_file}")
                return None, None
            
            print(f"🔍 Loading credentials from {self.credentials_file}")
            
            # Read encrypted data
            encrypted_data = self.credentials_file.read_bytes()
            print(f"📦 Read {len(encrypted_data)} bytes of encrypted data")
            
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
            import traceback
            traceback.print_exc()
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
                print(f"✅ Credentials deleted from {self.credentials_file}")
                return True
            else:
                print(f"ℹ️  No credentials to delete at {self.credentials_file}")
                return True
                
        except Exception as e:
            print(f"❌ Failed to delete credentials: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def credentials_exist(self) -> bool:
        """Check if credentials file exists."""
        exists = self.credentials_file.exists()
        # COMMENT OUT OR REMOVE THIS LINE:
        # print(f"🔍 Credentials exist at {self.credentials_file}: {exists}")
        return exists


# Singleton instance
_storage_instance = None


def get_credential_storage() -> CredentialStorage:
    """Get or create singleton credential storage instance."""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = CredentialStorage()
    return _storage_instance
