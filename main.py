import sys
import asyncio
import time
import config
import stt
import tts
import utils.helpers as helpers
import agents.memory as memory_agent
import api.routes as api_routes

# Configure UTF-8 encoding for Windows command prompt
helpers.configure_encoding()

def print_banner():
    """Prints startup banner with active AI stack telemetry."""
    groq_key = getattr(config, "GROQ_API_KEY", "")
    gemini_key = getattr(config, "GEMINI_API_KEY", "")
    
    if groq_key and groq_key != "your_groq_api_key_here":
        active_ai = "Groq AI (Ultra-Fast <0.3s Speed)"
        model_name = "llama-3.1-8b-instant"
    elif gemini_key and gemini_key != "your_gemini_api_key_here":
        active_ai = "Gemini Cloud AI"
        model_name = "gemini-3.1-flash-lite"
    else:
        active_ai = "Ollama Local AI"
        model_name = getattr(config, "OLLAMA_MODEL", "llama3.2")

    user_title = memory_agent.get_user_title()
    print("\n" + "=" * 60)
    print("                 J.A.R.V.I.S. ACTIVE")
    print(f"   Just A Rather Very Intelligent System - Assistant for {user_title}")
    print("=" * 60)
    print(f"Wake word:       '{config.WAKE_WORD}'")
    print(f"Primary AI:      {active_ai}")
    print(f"Active Model:    '{model_name}'")
    print(f"AI Sequence:     1. Groq  ->  2. Gemini  ->  3. Ollama")
    print("-" * 60)
    print("=" * 60 + "\n")

from agents.brain import JarvisBrain
brain = JarvisBrain()

def process_command(command_text: str):
    """Processes user input using JarvisBrain & speaks the response."""
    reply, actions = brain.think(command_text)
    if reply:
        tts.speak(reply)
    return {"response": reply, "actions": actions}

def main():
    print_banner()
    user_title = memory_agent.get_user_title()
    
    print("Select Input Mode:")
    print("1. Typing (Default)")
    print("2. Voice (Microphone)")
    
    try:
        choice = input("Enter choice (1 or 2): ").strip()
        input_mode = "voice" if choice == "2" else "typing"
    except Exception:
        input_mode = "typing"

    wake_word = config.WAKE_WORD
    
    if input_mode == "typing":
        print("[System] Typing mode selected.")
        tts.speak(f"Typing mode activated. Tell me what to do, {user_title}.")
        while True:
            try:
                user_input = input("\nJarvis > ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nExiting Jarvis.")
                tts.speak(f"Goodbye {user_title}.")
                break
                
            if not user_input:
                continue
                
            if any(exit_phrase in user_input.lower() for exit_phrase in ["goodbye jarvis", "exit", "quit", "shutdown"]):
                tts.speak(f"Goodbye {user_title}. Have a great day!")
                print("Exiting Jarvis.")
                break
                
            print(f"[Processing: '{user_input}']")
            try:
                process_command(user_input)
            except Exception as e:
                print(f"[Main Command Error] {e}")
                tts.speak(f"I had some trouble processing that command, {user_title}.")
    else:
        print("[System] Voice mode selected.")
        print("[System] Playing voice greeting...")
        tts.speak(f"System initialized. Voice mode activated. I am online and listening, {user_title}.")
        print("\n[System] ✅ Voice mode ready! Speak 'Jarvis' followed by your command.")
        
        wake_variants = [wake_word, "jarvas", "javas", "jervis", "gervis", "jarvice", "jarwis", "djarvis", "travis", "jarbus"]
        
        while True:
            print(f"\n[Listening for '{wake_word}'...]")
            heard = stt.listen(timeout=8, phrase_time_limit=10)
            if not heard:
                continue
                
            # Check for wake word or direct command
            command = heard
            for variant in wake_variants:
                if variant in heard:
                    command = heard.split(variant, 1)[-1].strip()
                    break
                    
            if command:
                print(f"[Voice Command: '{command}']")
                process_command(command)

if __name__ == "__main__":
    main()
