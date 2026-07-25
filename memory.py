import os
import json
import memory_manager

# Alias wrappers matching user's architecture specification
load_profile = memory_manager.load_profile
save_profile = memory_manager.save_profile
load_long_memory = memory_manager.load_long_memory
save_long_memory = memory_manager.save_long_memory
load_short_memory = memory_manager.load_short_memory
save_short_memory = memory_manager.save_short_memory

def remember_fact(key: str, value: str):
    """Explicit 'Remember...' command handler."""
    memory_manager.learn_fact(key, value)
    return f"Remembered {key} = {value}, Boss."

def forget_fact(key: str):
    """Explicit 'Forget...' command handler."""
    lm = memory_manager.load_long_memory()
    clean_key = key.strip().lower()
    if clean_key in lm.get("user_facts", {}):
        del lm["user_facts"][clean_key]
        memory_manager.save_long_memory(lm)
        print(f"[Memory] Forgot fact: {clean_key}")
        return f"Forgot {clean_key}, Boss."
    return f"No record found for {clean_key}, Boss."
