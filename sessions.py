import os
import json
from datetime import datetime
from config import SESSIONS_DIR

os.makedirs(SESSIONS_DIR, exist_ok=True)

def _session_path(name):
    return os.path.join(SESSIONS_DIR, f"{name}.json")

def list_sessions():
    """Return all saved session names."""
    files = os.listdir(SESSIONS_DIR)
    return [f.replace(".json", "") for f in files if f.endswith(".json")]

def load_session(name):
    """Load a session by name. Returns empty list if not found."""
    path = _session_path(name)
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

def save_session(name, messages):
    """Save messages to a named session file."""
    with open(_session_path(name), "w") as f:
        json.dump(messages, f, indent=2)

def delete_session(name):
    """Delete a session file."""
    path = _session_path(name)
    if os.path.exists(path):
        os.remove(path)
        return True
    return False

def new_session_name(): # gen name acc to dat time etc
    """Auto-generate a session name based on timestamp."""
    return datetime.now().strftime("session_%Y%m%d_%H%M%S")