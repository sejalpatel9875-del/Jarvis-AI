"""
Purpose:
Memory Agent & Preference Auto-Learning Subsystem for Jarvis AI OS.

Responsibilities:
- Detect personal preferences, company names, project names, and facts from user input
- Persist extracted preferences directly into SQLite
- Inject learned facts into the LLM system prompt for O(1) context recall
"""

import re
import memory.database as db
import memory.storage as storage

# In-Memory Buffer
memory = []

def save(message):
    """Saves a message into memory array and logs turn into SQLite DB."""
    memory.append(message)
    try:
        if isinstance(message, dict):
            u_msg = message.get("user", "") or message.get("content", "")
            a_msg = message.get("assistant", "") or message.get("response", "")
            if u_msg or a_msg:
                storage.save_conversation(str(u_msg), str(a_msg))
        else:
            storage.save_conversation(str(message), "")
    except Exception:
        pass

def history():
    """Returns the in-memory conversation history list."""
    return memory

def get_user_title() -> str:
    """Returns the user's title (e.g. 'Boss' or custom name)."""
    return storage.get_preference("user_name", "Boss") or "Boss"

def get_assistant_name() -> str:
    """Returns the assistant's name (e.g. 'Jarvis')."""
    return storage.get_preference("assistant_name", "Jarvis") or "Jarvis"

def update_profile(key: str, value: str):
    """Updates a preference entry in SQLite database."""
    storage.save_preference(key, value)
    print(f"[Memory Agent] Updated preference: {key} = {value}")

def remember_fact(key: str, value: str):
    """Saves a learned fact into preferences memory."""
    storage.save_preference(key, value)
    print(f"[Memory Agent] Learned & Persisted: {key} = {value}")
    return f"Remembered {key} = {value}, Boss."

def forget_fact(key: str):
    """Removes a fact from preference memory."""
    conn = db.get_connection()
    clean_key = key.strip().lower()
    conn.execute("DELETE FROM preferences WHERE key = ?", (clean_key,))
    conn.commit()
    conn.close()
    print(f"[Memory Agent] Forgot fact: {clean_key}")
    return f"Forgot {clean_key}, Boss."

def auto_learn_from_input(user_text: str) -> list:
    """Automatically detects personal facts, company info, and profile changes from user input."""
    text = user_text.strip()
    text_lower = text.lower().strip()
    learned = []
    
    # 1. "my company is X" / "mera company X hai"
    m = re.search(r'(?:my\s+company\s+is|mera\s+company)\s+(.+?)(?:\.|$)', text_lower)
    if m:
        comp = m.group(1).strip().title()
        update_profile("company_name", comp)
        learned.append(("company", f"company_name = {comp}"))

    # 2. "my project is X" / "my project name is X"
    m = re.search(r'(?:my\s+project\s+(?:name\s+)?is)\s+(.+?)(?:\.|$)', text_lower)
    if m:
        proj = m.group(1).strip().title()
        update_profile("project_name", proj)
        learned.append(("project", f"project_name = {proj}"))

    # 3. "mera favourite/favorite X Y hai" / "my favorite X is Y"
    m = re.search(r'(?:mera|meri|my)\s+(?:fav(?:ou?rite)?)\s+([\w\s]+?)\s+(?:is|hai)\s+(.+?)(?:\.|$)', text_lower)
    if m:
        key = f"favorite_{m.group(1).strip().replace(' ', '_')}"
        val = m.group(2).strip()
        remember_fact(key, val)
        learned.append(("learn", f"{key} = {val}"))
        
    # 4. "my name is X" / "mera naam X hai" / "call me X"
    m = re.search(r'(?:my\s+name\s+is|mera\s+naam|call\s+me)\s+(\w+)', text_lower)
    if m:
        name = m.group(1).strip().capitalize()
        update_profile("user_name", name)
        learned.append(("profile", f"user_name = {name}"))
        
    return learned

def get_memory_context() -> str:
    """Returns formatted memory string containing stored user preferences for AI system instruction."""
    user_title = get_user_title()
    lang = storage.get_preference("language", "Hinglish")
    company = storage.get_preference("company_name", "")
    project = storage.get_preference("project_name", "")

    ctx = f"User Name/Title: {user_title}\nPreferred Language: {lang}"
    if company:
        ctx += f"\nUser Company: {company}"
    if project:
        ctx += f"\nActive Project: {project}"
    return ctx
