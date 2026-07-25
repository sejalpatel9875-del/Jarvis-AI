import os
import re
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_DIR = os.path.join(BASE_DIR, "memory")

PROFILE_FILE = os.path.join(MEMORY_DIR, "profile.json")
SHORT_MEMORY_FILE = os.path.join(MEMORY_DIR, "short_memory.json")
LONG_MEMORY_FILE = os.path.join(MEMORY_DIR, "long_memory.json")

# Ensure memory directory exists
os.makedirs(MEMORY_DIR, exist_ok=True)

DEFAULT_PROFILE = {
    "assistant_name": "Jarvis",
    "user_name": "Boss",
    "preferred_language": "Hinglish (Hindi + English)",
    "city": "",
    "timezone": ""
}

DEFAULT_SHORT_MEMORY = {
    "recent_turns": [],
    "last_summary": ""
}

DEFAULT_LONG_MEMORY = {
    "user_facts": {},
    "projects": {},
    "preferences": [],
    "custom_contacts": {
        "mom": "+919999999999",
        "dad": "+918888888888"
    }
}

# ==========================================
# PROFILE MANAGEMENT
# ==========================================

def load_profile() -> dict:
    """Loads profile from memory/profile.json."""
    if not os.path.exists(PROFILE_FILE):
        save_profile(DEFAULT_PROFILE)
        return DEFAULT_PROFILE
    try:
        with open(PROFILE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not data.get("user_name"):
                data["user_name"] = "Boss"
            if not data.get("assistant_name"):
                data["assistant_name"] = "Jarvis"
            return data
    except Exception as e:
        print(f"[Memory Error] Failed to load profile: {e}")
        return DEFAULT_PROFILE

def save_profile(data: dict):
    """Saves profile data to memory/profile.json."""
    try:
        with open(PROFILE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[Memory Error] Failed to save profile: {e}")

def get_user_title() -> str:
    """Returns the user's title (e.g. 'Boss' or 'Kajal')."""
    prof = load_profile()
    return prof.get("user_name", "Boss") or "Boss"

def get_assistant_name() -> str:
    """Returns the assistant's name (e.g. 'Jarvis')."""
    prof = load_profile()
    return prof.get("assistant_name", "Jarvis") or "Jarvis"

def update_profile(key: str, value: str):
    """Updates a field in profile.json."""
    prof = load_profile()
    prof[key.strip().lower()] = value.strip()
    save_profile(prof)
    print(f"[Profile] Updated profile: {key} = {value}")

# ==========================================
# SHORT-TERM MEMORY (Conversations)
# ==========================================

def load_short_memory() -> dict:
    """Loads short-term memory (recent conversation turns)."""
    if not os.path.exists(SHORT_MEMORY_FILE):
        save_short_memory(DEFAULT_SHORT_MEMORY)
        return DEFAULT_SHORT_MEMORY
    try:
        with open(SHORT_MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_SHORT_MEMORY

def save_short_memory(data: dict):
    """Saves short-term memory."""
    try:
        with open(SHORT_MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[Memory Error] Failed to save short memory: {e}")

def add_short_turn(user_msg: str, assistant_reply: str):
    """Appends a conversation turn to short-term memory (max 10 recent turns)."""
    sm = load_short_memory()
    turns = sm.get("recent_turns", [])
    turns.append({"user": user_msg, "assistant": assistant_reply})
    sm["recent_turns"] = turns[-10:]
    save_short_memory(sm)

# ==========================================
# LONG-TERM MEMORY (Facts, Projects, Contacts)
# ==========================================

def load_long_memory() -> dict:
    """Loads long-term memory."""
    if not os.path.exists(LONG_MEMORY_FILE):
        save_long_memory(DEFAULT_LONG_MEMORY)
        return DEFAULT_LONG_MEMORY
    try:
        with open(LONG_MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_LONG_MEMORY

def save_long_memory(data: dict):
    """Saves long-term memory."""
    try:
        with open(LONG_MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"[Memory Error] Failed to save long memory: {e}")

def learn_fact(key: str, value: str):
    """Saves a learned fact into long-term memory."""
    lm = load_long_memory()
    lm["user_facts"][key.strip().lower()] = value.strip()
    save_long_memory(lm)
    print(f"[Memory] Learned & Persisted: {key} = {value}")

def add_contact(name: str, number: str):
    """Adds a custom contact number into long-term memory."""
    lm = load_long_memory()
    phone = number.strip().replace(" ", "").replace("-", "")
    lm["custom_contacts"][name.strip().lower()] = phone
    save_long_memory(lm)
    print(f"[Memory] Contact added: {name} = {phone}")

def add_project(project_name: str, details: str):
    """Saves a project into long-term memory."""
    lm = load_long_memory()
    lm["projects"][project_name.strip().lower()] = details.strip()
    save_long_memory(lm)
    print(f"[Memory] Project saved: {project_name} = {details}")

# Legacy compatibility wrapper
def load_memory() -> dict:
    return load_long_memory()

def save_memory(data: dict):
    save_long_memory(data)

def auto_learn_from_input(user_text: str) -> list:
    """
    Automatically detects personal facts, contacts, and profile changes from user input.
    """
    text = user_text.strip()
    text_lower = text.lower().strip()
    learned = []
    
    # "mera favourite/favorite X Y hai" / "my favorite X is Y"
    m = re.search(r'(?:mera|meri|my)\s+(?:fav(?:ou?rite)?)\s+([\w\s]+?)\s+(?:is|hai)\s+(.+?)(?:\.|$)', text_lower)
    if m:
        key = f"favorite_{m.group(1).strip().replace(' ', '_')}"
        val = m.group(2).strip()
        learn_fact(key, val)
        learned.append(("learn", f"{key} = {val}"))
        
    # "my name is X" / "mera naam X hai" / "call me X"
    m = re.search(r'(?:my\s+name\s+is|mera\s+naam|call\s+me)\s+(\w+)', text_lower)
    if m:
        name = m.group(1).strip().capitalize()
        update_profile("user_name", name)
        learned.append(("profile", f"user_name = {name}"))
    
    # "I live in X" / "main X mein rehta hoon"
    m = re.search(r'(?:i\s+live\s+in|main\s+(.+?)\s+mein\s+rehta)', text_lower)
    if m:
        city = m.group(1).strip().capitalize()
        update_profile("city", city)
        learned.append(("profile", f"city = {city}"))
        
    # "save contact X Y" / "contact X Y"
    m = re.search(r'(?:save\s+)?contact\s+(\w+)\s+(\+?\d[\d\s\-]{8,})', text_lower)
    if m:
        name = m.group(1).strip()
        number = m.group(2).strip()
        add_contact(name, number)
        learned.append(("add_contact", f"{name} = {number}"))
        
    return learned
