# modules/preferences.py
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any

PREFERENCES_FILE = Path.home() / ".email_automation_preferences.json"

DEFAULT_PREFERENCES = {
    "email_tone": "formal",
    "sender_name": "Donil",
    "cc_emails": "",
    "bcc_emails": "",
    "subject_prefix": "",
    "default_recipient": "",  # ✅ NEW
    "default_subject": "",     # ✅ NEW
}


def save_preferences(preferences: Dict[str, Any]) -> bool:
    """Save user preferences to local JSON file."""
    try:
        with open(PREFERENCES_FILE, "w") as f:
            json.dump(preferences, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving preferences: {e}")
        return False


def load_preferences() -> Dict[str, Any]:
    """Load user preferences from local JSON file."""
    try:
        if PREFERENCES_FILE.exists():
            with open(PREFERENCES_FILE, "r") as f:
                saved_prefs = json.load(f)
                # Merge with defaults to handle new fields
                return {**DEFAULT_PREFERENCES, **saved_prefs}
        return DEFAULT_PREFERENCES.copy()
    except Exception as e:
        print(f"Error loading preferences: {e}")
        return DEFAULT_PREFERENCES.copy()


def clear_preferences() -> bool:
    """Clear saved preferences."""
    try:
        if PREFERENCES_FILE.exists():
            PREFERENCES_FILE.unlink()
        return True
    except Exception as e:
        print(f"Error clearing preferences: {e}")
        return False


def get_preference(key: str, default: Any = None) -> Any:
    """Get a specific preference value."""
    prefs = load_preferences()
    return prefs.get(key, default)


def preferences_exist() -> bool:
    """Check if preferences file exists."""
    return PREFERENCES_FILE.exists()
