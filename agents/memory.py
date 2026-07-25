import re
import memory.database as db

def get_user_title() -> str:
    """Returns the user's title (e.g. 'Boss')."""
    return db.get_profile_value("user_name", "Boss") or "Boss"

def get_assistant_name() -> str:
    """Returns the assistant's name (e.g. 'Jarvis')."""
    return db.get_profile_value("assistant_name", "Jarvis") or "Jarvis"

def update_profile(key: str, value: str):
    """Updates a profile entry in SQLite database."""
    db.set_profile_value(key, value)
    print(f"[Memory Agent] Updated profile: {key} = {value}")

def remember_fact(key: str, value: str):
    """Saves a learned fact into long-term memory."""
    db.save_user_fact(key, value)
    print(f"[Memory Agent] Learned & Persisted: {key} = {value}")
    return f"Remembered {key} = {value}, Boss."

def forget_fact(key: str):
    """Removes a fact from long-term memory."""
    facts = db.get_all_user_facts()
    clean_key = key.strip().lower()
    if clean_key in facts:
        conn = db.get_connection()
        conn.execute("DELETE FROM user_facts WHERE fact_key = ?", (clean_key,))
        conn.commit()
        conn.close()
        print(f"[Memory Agent] Forgot fact: {clean_key}")
        return f"Forgot {clean_key}, Boss."
    return f"No record found for {clean_key}, Boss."

def auto_learn_from_input(user_text: str) -> list:
    """Automatically detects personal facts, contacts, and profile changes from user input."""
    text = user_text.strip()
    text_lower = text.lower().strip()
    learned = []
    
    # "mera favourite/favorite X Y hai" / "my favorite X is Y"
    m = re.search(r'(?:mera|meri|my)\s+(?:fav(?:ou?rite)?)\s+([\w\s]+?)\s+(?:is|hai)\s+(.+?)(?:\.|$)', text_lower)
    if m:
        key = f"favorite_{m.group(1).strip().replace(' ', '_')}"
        val = m.group(2).strip()
        remember_fact(key, val)
        learned.append(("learn", f"{key} = {val}"))
        
    # "my name is X" / "mera naam X hai" / "call me X"
    m = re.search(r'(?:my\s+name\s+is|mera\s+naam|call\s+me)\s+(\w+)', text_lower)
    if m:
        name = m.group(1).strip().capitalize()
        update_profile("user_name", name)
        learned.append(("profile", f"user_name = {name}"))
    
    # "save contact X Y" / "contact X Y"
    m = re.search(r'(?:save\s+)?contact\s+(\w+)\s+(\+?\d[\d\s\-]{8,})', text_lower)
    if m:
        name = m.group(1).strip()
        number = m.group(2).strip()
        db.save_contact(name, number)
        learned.append(("add_contact", f"{name} = {number}"))
        
    return learned

def get_memory_context() -> str:
    """Returns formatted memory string for AI system instruction."""
    user_title = get_user_title()
    facts = db.get_all_user_facts()
    facts_str = ", ".join([f"{k}: {v}" for k, v in facts.items()])
    return f"User Title: {user_title}\nSaved Facts: [{facts_str}]" if facts_str else f"User Title: {user_title}"
