import sys
import asyncio
import time
import config
import realtime
import automation
import memory_manager

# Module imports for Cloud Gemini Dual-Model Chat & Google Gemini TTS
import stt
import tts
from chatbot import Chatbot

# Reconfigure stdout/stderr to support printing UTF-8 characters (like Hindi) on Windows command prompt
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
if sys.stderr.encoding != 'utf-8':
    try:
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

def print_banner():
    # Determine active primary AI Provider dynamically
    groq_key = getattr(config, "GROQ_API_KEY", "")
    gemini_key = getattr(config, "GEMINI_API_KEY", "")
    
    if groq_key and groq_key != "your_groq_api_key_here":
        active_ai = "Groq AI (Ultra-Fast <0.3s Target Speed)"
        model_name = "llama-3.1-8b-instant"
    elif gemini_key and gemini_key != "your_gemini_api_key_here":
        active_ai = "Gemini Cloud AI"
        model_name = "gemini-3.1-flash-lite"
    else:
        active_ai = "Ollama Local AI"
        model_name = getattr(config, "OLLAMA_MODEL", "llama3.2")

    user_title = memory_manager.get_user_title()
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

def check_live_intent(command: str, is_typing_mode: bool = False) -> bool:
    """
    Checks if the command indicates an intent to enter the Live session.
    If in typing mode, only explicit triggers launch live session.
    """
    cmd = command.lower()
    
    # Explicit commands to go live
    live_triggers = [
        "live mode", "realtime mode", "go live", 
        "start live", "talk to me live", "realtime chat",
        "interactive mode"
    ]
    for trigger in live_triggers:
        if trigger in cmd:
            return True
            
    # Grounding/live info triggers (weather, news, real-time current events)
    # We only switch automatically if we are NOT in typing mode.
    if not is_typing_mode:
        grounding_triggers = [
            "weather", "news", "current events", "latest news",
            "who is the ceo of", "current price of", "temperature",
            "right now", "what is the date", "today's news"
        ]
        for trigger in grounding_triggers:
            if trigger in cmd:
                return True
                
    return False

def parse_action_tags(response_text: str):
    """
    Parses prefix tags like [ACTION: play_music | perfect] and returns a list of tuples (intent, argument) and the remaining clean text.
    """
    import re
    pattern = r'\[ACTION:\s*(\w+)\s*\|\s*(.*?)\]'
    matches = list(re.finditer(pattern, response_text))
    
    actions = []
    clean_text = response_text
    
    for m in matches:
        intent = m.group(1).strip()
        argument = m.group(2).strip()
        actions.append((intent, argument))
        # Remove the tag from the text
        clean_text = clean_text.replace(m.group(0), "")
        
    return actions, clean_text.strip()

def parse_input_commands_fallback(command_text: str):
    """
    Parses user input directly for multitasking triggers when LLM response omits action tags.
    Handles 'play X, open Y, close Z, search W, send whatsapp A:B, lock pc, screenshot' sequentially.
    """
    import re
    text = command_text.lower().strip()
    
    actions = []
    
    # 1. Parse Image Generation, Screen Vision, PC Lock, and Screenshot Fallbacks first
    if any(kw in text for kw in ["describe screen", "what's on my screen", "what is on my screen", "read screen"]):
        actions.append(("describe_screen", ""))
    elif any(kw in text for kw in ["lock pc", "lock screen", "lock computer"]):
        actions.append(("lock_pc", ""))
    elif "screenshot" in text or "capture screen" in text:
        actions.append(("take_screenshot", ""))
        
    img_match = re.search(r'(?:generate|create|draw|make)\s+(?:an?\s+)?image\s+(?:of\s+)?(.*)', text)
    if img_match:
        actions.append(("generate_image", img_match.group(1).strip()))
        
    wiki_match = re.search(r'wikipedia\s+(?:search\s+)?(?:for\s+)?(.*)', text)
    if wiki_match:
        actions.append(("search_wikipedia", wiki_match.group(1).strip()))
        
    # 2. Parse WhatsApp Messaging Fallbacks
    # Pattern A: "send message on whatsapp <message> to <recipient>"
    whatsapp_match_a = re.search(r'whatsapp\s+(?:message\s+)?(?:saying\s+|with\s+)?(.*?)\s+to\s+(\w+)', text)
    # Pattern B: "send message to <recipient> on whatsapp <message>"
    whatsapp_match_b = re.search(r'to\s+(\w+)\s+(?:on\s+)?whatsapp\s+(?:saying\s+|with\s+)?(.*)', text)
    # Pattern C: "whatsapp <recipient> saying <message>"
    whatsapp_match_c = re.search(r'whatsapp\s+(\w+)\s+(?:saying\s+|message\s+|with\s+)?(.*)', text)
    
    if whatsapp_match_a:
        msg = whatsapp_match_a.group(1).strip().replace("hi to", "hi")
        recipient = whatsapp_match_a.group(2).strip()
        actions.append(("send_whatsapp", f"{recipient}:{msg}"))
    elif whatsapp_match_b:
        recipient = whatsapp_match_b.group(1).strip()
        msg = whatsapp_match_b.group(2).strip()
        actions.append(("send_whatsapp", f"{recipient}:{msg}"))
    elif whatsapp_match_c and not any(kw in text for kw in ["open", "close"]):
        recipient = whatsapp_match_c.group(1).strip()
        msg = whatsapp_match_c.group(2).strip()
        actions.append(("send_whatsapp", f"{recipient}:{msg}"))
        
    # 3. Process Verb Trigger Tokens
    clean_text = text.replace(",", " ").replace(" and ", " ").replace(" aur ", " ").strip()
    clean_text = re.sub(r'\b(start|launch|run)\b', 'open', clean_text)
    tokens = clean_text.split()
    
    current_intent = None
    current_arg_tokens = []
    
    i = 0
    while i < len(tokens):
        token = tokens[i]
        
        # Check for active verb triggers
        if token in ["play", "open", "close", "search", "google", "volume", "brightness"]:
            if current_intent:
                arg_str = " ".join(current_arg_tokens).strip()
                # Skip duplicate app or whatsapp intents already caught above
                if not (current_intent == "open_app" and arg_str == "whatsapp" and any(a[0] == "send_whatsapp" for a in actions)):
                    actions.append((current_intent, arg_str))
                current_arg_tokens = []
                
            if token == "play":
                current_intent = "play_music"
            elif token == "close":
                current_intent = "close_app"
            elif token == "open":
                if i + 1 < len(tokens) and tokens[i+1] == "youtube":
                    current_intent = "open_youtube"
                    i += 1
                elif i + 1 < len(tokens) and tokens[i+1] == "browser":
                    current_intent = "open_browser"
                    i += 1
                else:
                    current_intent = "open_app"
            elif token in ["search", "google"]:
                current_intent = "search_google"
                if token == "search" and i + 1 < len(tokens) and tokens[i+1] == "google":
                    i += 1
            elif token == "volume":
                current_intent = "adjust_volume"
            elif token == "brightness":
                current_intent = "adjust_brightness"
        else:
            if current_intent:
                current_arg_tokens.append(token)
        i += 1
        
    if current_intent:
        arg_str = " ".join(current_arg_tokens).strip()
        if not (current_intent == "open_app" and arg_str == "whatsapp" and any(a[0] == "send_whatsapp" for a in actions)):
            actions.append((current_intent, arg_str))
            
    # Clean duplicates while preserving order
    unique_actions = []
    seen = set()
    for act in actions:
        if act not in seen:
            unique_actions.append(act)
            seen.add(act)
            
    return unique_actions

def process_user_command(command_text: str, chatbot: Chatbot, is_typing_mode: bool = False) -> bool:
    """
    Orchestrates command execution in exactly 1 API call (or 0 API calls for local automations).
    Returns True when the command processing completes.
    """
    # 0. Auto-learn from user input (deterministic regex, no LLM dependency)
    try:
        import memory_manager
        memory_manager.auto_learn_from_input(command_text)
    except Exception as e:
        print(f"[Auto-Learn Error] {e}")

    # 1. Check for Live session intent first (so voice questions enter live mode)
    if check_live_intent(command_text, is_typing_mode):
        tts.speak("Connecting you to the live session, Kajal maam. One moment.")
        try:
            asyncio.run(realtime.start_realtime_session())
        except Exception as e:
            print(f"[Main Error] Live session failed: {e}")
            tts.speak("Sorry Kajal maam, I couldn't establish the live connection.")
        return True

    # 2. Fast Zero-Cost Tool Router (Math, Desktop Folders, System Controls in <0.005s)
    try:
        import tool_router
        is_handled, tool_reply = tool_router.route_local_tool(command_text)
        if is_handled and tool_reply:
            tts.speak(tool_reply)
            return True
    except Exception as ex:
        print(f"[Tool Router Warning] {ex}")

    # 3. Call Chatbot Brain (1 API call)
    reply = chatbot.ask(command_text)
    
    # Check if the chatbot output a rate limit error or empty response
    if not reply or "Sorry Kajal maam" in reply:
        tts.speak(reply)
        return True

    # 4. Parse Action Tags from response
    actions, clean_text = parse_action_tags(reply)
    
    if not actions:
        # Fallback to direct input parsing if the local LLM response omitted action tags
        fallback_actions = parse_input_commands_fallback(command_text)
        if fallback_actions:
            print(f"[Combined Router Fallback] Extracted Fallback Actions: {fallback_actions}")
            actions = fallback_actions
            clean_text = reply
            
    if actions:
        print(f"[Combined Router] Extracted Multitasking Actions: {actions}")
        # Speak voice confirmation to user
        if not clean_text or clean_text.startswith("[ACTION:"):
            user_title = memory_manager.get_user_title()
            clean_text = f"Sure {user_title}, executing your command now."
        tts.speak(clean_text)
        
        # Execute each automation action sequentially
        for intent, arg in actions:
            try:
                if intent == "play_music":
                    automation.play_song(arg)
                elif intent == "open_app":
                    automation.open_app(arg)
                elif intent == "close_app":
                    automation.close_app(arg)
                elif intent == "lock_pc":
                    automation.lock_pc()
                elif intent == "take_screenshot":
                    automation.take_screenshot()
                elif intent == "generate_image":
                    img_res = automation.generate_image(arg)
                    tts.speak(img_res)
                elif intent == "search_wikipedia":
                    wiki_res = automation.search_wikipedia(arg)
                    tts.speak(wiki_res)
                elif intent == "describe_screen":
                    vision_res = automation.describe_screen(chatbot)
                    tts.speak(vision_res)
                elif intent == "open_website":
                    automation.open_website(arg)
                elif intent == "search_google":
                    automation.search_google(arg)
                elif intent == "search_chatgpt":
                    automation.search_chatgpt(arg)
                    # If hybrid mode is active, fetch real-time grounded search results from cloud Gemini API
                    if getattr(config, "USE_LOCAL_AI", False) and getattr(config, "HYBRID_MODE", True) and cloud_chatbot:
                        print(f"[Hybrid Mode] Fetching search results for: '{arg}' via Cloud Gemini API...")
                        cloud_reply = cloud_chatbot.ask(command_text)
                        tts.speak(cloud_reply)
                elif intent == "adjust_volume":
                    automation.route_automation(f"volume {arg}")
                elif intent == "adjust_brightness":
                    automation.route_automation(f"brightness {arg}")
                elif intent == "open_youtube":
                    automation.open_youtube()
                elif intent == "open_browser":
                    automation.open_browser()
                elif intent == "send_whatsapp":
                    if ":" in arg:
                        recipient, msg = arg.split(":", 1)
                    else:
                        recipient, msg = arg, "Hello!"
                    automation.send_whatsapp_message(recipient, msg)
                elif intent == "send_instagram":
                    if ":" in arg:
                        recipient, msg = arg.split(":", 1)
                    else:
                        recipient, msg = arg, "Hello!"
                    automation.send_instagram_message(recipient, msg)
                elif intent == "learn":
                    if ":" in arg:
                        k, v = arg.split(":", 1)
                        import memory_manager
                        memory_manager.learn_fact(k, v)
                elif intent == "add_contact":
                    import re as _re
                    import memory_manager
                    phone_match = _re.search(r'(\+?\d[\d\s\-]{7,})', arg)
                    name_match = _re.search(r'(?:name[:\s]*)?([a-zA-Z]+)', arg)
                    if phone_match and name_match:
                        contact_name = name_match.group(1).strip().lower()
                        contact_num = _re.sub(r'[\s\-]', '', phone_match.group(1).strip())
                        memory_manager.add_contact(contact_name, contact_num)
                    elif ":" in arg:
                        name, num = arg.split(":", 1)
                        memory_manager.add_contact(name.strip(), num.strip())
                elif intent == "update_personality":
                    import memory_manager
                    memory_manager.update_personality(arg)
                elif intent == "shutdown_pc":
                    automation.shutdown_pc()
                elif intent == "restart_pc":
                    automation.restart_pc()
                elif intent == "sleep_pc":
                    automation.sleep_pc()
                elif intent == "logoff_pc":
                    automation.logoff_pc()
                elif intent == "cancel_shutdown":
                    automation.cancel_shutdown()
                elif intent == "type_text":
                    automation.type_text(arg)
                elif intent == "press_key":
                    automation.press_key(arg)
            except Exception as ex:
                print(f"[Action Execution Error] {ex}")
    else:
        # General chat - just speak the reply!
        tts.speak(reply)
        
    return True

def main():
    print_banner()
    
    # 1. Initialize chatbot brain
    try:
        chatbot = Chatbot()
    except Exception as e:
        print(f"[Main Error] Failed to initialize Gemini Chatbot: {e}")
        print("Please check your GEMINI_API_KEY in the .env file.")
        sys.exit(1)
        
    # 2. Select Input Mode (Default to Typing)
    print("\nSelect Input Mode:")
    print("1. Typing (Default)")
    print("2. Voice (Microphone)")
    try:
        choice = input("Enter choice (1 or 2): ").strip()
    except (KeyboardInterrupt, EOFError):
        choice = "1"
        
    input_mode = "typing"
    if choice == "2":
        input_mode = "voice"
        print("[System] Voice mode selected.")
    else:
        print("[System] Typing mode selected.")
        
    wake_word = config.WAKE_WORD
    
    try:
        if input_mode == "typing":
            user_title = memory_manager.get_user_title()
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
                    
                # Check for exit command
                if any(exit_phrase in user_input.lower() for exit_phrase in ["goodbye jarvis", "exit", "quit", "shutdown"]):
                    tts.speak(f"Goodbye {user_title}. Have a great day!")
                    print("Exiting Jarvis.")
                    break
                    
                print(f"[Processing: '{user_input}']")
                
                try:
                    process_user_command(user_input, chatbot, is_typing_mode=True)
                except Exception as e:
                    print(f"[Main Command Error] {e}")
                    user_title = memory_manager.get_user_title()
                    tts.speak(f"I had some trouble processing that command, {user_title}. Could you try again?")
                    
        else:
            # Voice / Mic Mode — Instant Startup
            print("[System] Playing voice greeting...")
            user_title = memory_manager.get_user_title()
            tts.speak(f"System initialized. Voice mode activated. I am online and listening, {user_title}.")
            print("\n[System] ✅ Voice mode ready! Speak 'Jarvis' followed by your command.")
            
            # Fuzzy wake word variants (Whisper often misrecognizes "jarvis")
            wake_variants = [
                wake_word,        # jarvis
                "jarvas", "javas", "jervis", "gervis", "jarves",
                "service", "jarvice", "jarwis", "djarvis", "jarvi",
                "travis", "jarbus", "jarbis", "darvis", "harvest",
                "j.a.r.v.i.s", "j.a.r.v.i.s.",
            ]
            
            def detect_wake_word(text: str):
                """
                Returns (True, command_after_wake_word) if wake word detected.
                Uses fuzzy matching to handle Whisper misrecognitions.
                """
                words = text.lower().split()
                for i, word in enumerate(words):
                    # Check exact match with variants
                    for variant in wake_variants:
                        if variant in word:
                            # Extract command after wake word
                            remaining = " ".join(words[i+1:]).strip()
                            return True, remaining
                return False, text
            
            while True:
                # Continuously listen
                print(f"\n[Listening for '{wake_word}'...]")
                heard = stt.listen(timeout=8, phrase_time_limit=10)
                
                if not heard:
                    continue
                
                # 1. Check for wake word (fuzzy matching)
                wake_detected, command = detect_wake_word(heard)
                
                # Action words that indicate a user command even if wake word wasn't explicitly pronounced
                action_keywords = [
                    "open", "close", "send", "message", "search", "play", "lock",
                    "shutdown", "restart", "sleep", "take", "screenshot", "brightness",
                    "volume", "karo", "karke", "usmein", "kaise", "batao", "bataiye", "banao", "kare"
                ]
                is_actionable = wake_detected or any(w in heard for w in action_keywords)
                
                if is_actionable:
                    target_cmd = command if (wake_detected and command) else heard
                    print(f"\n[Voice Command Detected: '{target_cmd}']")
                    
                    if wake_detected and not command:
                        # Just wake word spoken — prompt user for command
                        tts.speak("Yes, Kajal maam?")
                        print("[Listening for command...]")
                        target_cmd = stt.listen(timeout=8, phrase_time_limit=15)
                        if not target_cmd:
                            print("[No command received]")
                            tts.speak("Kajal maam, aapki aavaj nahi aa rahi. Please repeat.")
                            continue
                    
                    print(f"[Processing Command: '{target_cmd}']")
                    
                    # Check for exit
                    if any(ep in target_cmd for ep in ["goodbye jarvis", "exit", "quit", "shutdown jarvis"]):
                        tts.speak("Goodbye Kajal maam. Have a great day!")
                        print("Exiting Jarvis.")
                        break
                    
                    # First try direct automation (for simple 1-2 word commands)
                    auto_result = automation.route_automation(target_cmd)
                    if auto_result:
                        print(f"[Direct Automation] {auto_result}")
                        tts.speak(auto_result)
                    else:
                        # Send to AI Chatbot for multi-intent action parsing and execution
                        try:
                            process_user_command(target_cmd, chatbot, is_typing_mode=False)
                        except Exception as e:
                            print(f"[Command Error] {e}")
                            tts.speak("Sorry Kajal maam, error processing command. Please try again.")
                
                time.sleep(0.1)
                
    except KeyboardInterrupt:
        print("\n[Ctrl+C] Shutting down J.A.R.V.I.S. gracefully.")
        tts.speak("Shutting down now. Goodbye Kajal maam.")
    except Exception as e:
        print(f"[Main Critical Error] {e}")
        tts.speak("Sorry Kajal maam, I encountered a critical error.")

if __name__ == "__main__":
    main()
