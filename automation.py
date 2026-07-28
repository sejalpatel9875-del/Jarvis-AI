import os
import sys
import platform
import subprocess
import webbrowser
import urllib.parse
import re
import time

# Reconfigure stdout/stderr to support printing UTF-8 characters on Windows command prompt
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def open_browser(url: str = None):
    """Opens the default web browser to the specified URL or Google homepage."""
    target_url = url or "https://www.google.com"
    print(f"[Automation] Opening browser to: {target_url}")
    webbrowser.open(target_url)
    return f"Opening browser to {target_url}"

def open_youtube():
    """Opens YouTube in the default browser."""
    print("[Automation] Opening YouTube")
    webbrowser.open("https://www.youtube.com")
    return "Opening YouTube"

def play_song(song_name: str):
    """Searches for and auto-plays a song on YouTube directly without blocking main thread."""
    clean_name = song_name.strip()
    print(f"[Automation] 🎵 Playing song: '{clean_name}' on YouTube...")
    
    import threading
    def play_thread():
        import requests
        safe_query = urllib.parse.quote(clean_name)
        url = f"https://www.youtube.com/results?search_query={safe_query}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        
        # 1. Direct YouTube Video Extraction (Instant Auto-Play)
        try:
            res = requests.get(url, headers=headers, timeout=4)
            vids = re.findall(r'"videoId":"([^"]+)"', res.text)
            if vids:
                direct_url = f"https://www.youtube.com/watch?v={vids[0]}"
                print(f"[Automation] 🚀 Launching direct video auto-play: {direct_url}")
                webbrowser.open(direct_url)
                return
        except Exception as ex:
            print(f"[Automation Warning] Direct video match failed: {ex}")
            
        # 2. Pywhatkit fallback
        try:
            import pywhatkit
            pywhatkit.playonyt(clean_name)
            return
        except Exception:
            pass
            
        # 3. Search page fallback
        webbrowser.open(url)
            
    threading.Thread(target=play_thread, daemon=True).start()
    return f"Playing {clean_name} on YouTube"

def set_brightness(level: int):
    """Sets screen brightness (0-100) using screen-brightness-control on Windows."""
    try:
        import screen_brightness_control as sbc
        sbc.set_brightness(level)
        print(f"[Automation] Screen brightness set to {level}%")
        return f"Setting screen brightness to {level} percent"
    except Exception as e:
        print(f"[Automation Error] Failed to set brightness: {e}")
        return "Sorry Kajal maam, I couldn't adjust the screen brightness."

def change_brightness(offset: int):
    """Adjusts screen brightness relatively (e.g. +10 or -10)."""
    try:
        import screen_brightness_control as sbc
        current = sbc.get_brightness()
        if isinstance(current, list):
            current = current[0]
        new_val = max(0, min(100, current + offset))
        sbc.set_brightness(new_val)
        print(f"[Automation] Screen brightness adjusted to {new_val}% (offset {offset}%)")
        return f"Adjusting screen brightness to {new_val} percent"
    except Exception as e:
        print(f"[Automation Error] Failed to adjust brightness: {e}")
        return "Sorry Kajal maam, I couldn't adjust the screen brightness."

def set_volume(level: float):
    """Sets system master volume (0.0 to 1.0) using pycaw on Windows."""
    try:
        from pycaw.pycaw import AudioUtilities
        devices = AudioUtilities.GetSpeakers()
        volume = devices.EndpointVolume
        val = max(0.0, min(1.0, level))
        volume.SetMasterVolumeLevelScalar(val, None)
        print(f"[Automation] Master volume set to {int(val * 100)}%")
        return f"Setting system volume to {int(val * 100)} percent"
    except Exception as e:
        print(f"[Automation Error] Failed to set volume: {e}")
        return "Sorry Kajal maam, I couldn't adjust the system volume."

def change_volume(offset: float):
    """Adjusts system volume relatively (e.g. +0.1 or -0.1)."""
    try:
        from pycaw.pycaw import AudioUtilities
        devices = AudioUtilities.GetSpeakers()
        volume = devices.EndpointVolume
        current = volume.GetMasterVolumeLevelScalar()
        new_val = max(0.0, min(1.0, current + offset))
        volume.SetMasterVolumeLevelScalar(new_val, None)
        print(f"[Automation] Master volume adjusted to {int(new_val * 100)}% (offset {int(offset * 100)}%)")
        return f"Adjusting system volume to {int(new_val * 100)} percent"
    except Exception as e:
        print(f"[Automation Error] Failed to adjust volume: {e}")
        return "Sorry Kajal maam, I couldn't adjust the system volume."

def open_website(site_name: str):
    """Opens a website in the default browser cleanly without invalid 404 URLs."""
    site = site_name.strip().lower()
    
    # Check keyword mappings first
    if "whatsapp" in site:
        url = "https://web.whatsapp.com"
        site_name = "WhatsApp Web"
    elif any(k in site for k in ["chatgpt", "chat gpt", "gpt", "chat ppt"]):
        url = "https://chatgpt.com"
        site_name = "ChatGPT"
    elif "instagram" in site or "insta" in site:
        url = "https://www.instagram.com"
        site_name = "Instagram"
    elif "youtube" in site:
        url = "https://www.youtube.com"
        site_name = "YouTube"
    elif "google" in site or "chrome" in site:
        url = "https://www.google.com"
        site_name = "Google"
    elif "github" in site:
        url = "https://github.com"
        site_name = "GitHub"
    elif "gmail" in site or "mail" in site:
        url = "https://mail.google.com"
        site_name = "Gmail"
    elif "spotify" in site:
        url = "https://open.spotify.com"
        site_name = "Spotify"
    elif re.search(r'^[a-z0-9\-\.]+\.[a-z]{2,5}$', site.replace(" ", "")):
        clean_site = site.replace(" ", "")
        url = clean_site if clean_site.startswith("http") else "https://" + clean_site
    else:
        # If it's an unrecognized sentence or query, search Google instead of opening a broken www.garbage.com URL!
        print(f"[Automation] Unrecognized domain '{site_name}'. Performing Google search...")
        return search_google(site_name)
        
    print(f"[Automation] Opening website: {url}")
    webbrowser.open(url)
    return f"Opening {site_name}"

def auto_press_enter(delay: float):
    """Spawns a background thread to press enter after a delay, completing the automated send."""
    import threading
    def work():
        time.sleep(delay)
        try:
            import pyautogui
            pyautogui.press('enter')
            print("[Automation] 🚀 Pressed Enter key to automatically send message.")
        except Exception as e:
            print(f"[Automation Error] Auto-send failed: {e}")
    threading.Thread(target=work, daemon=True).start()

def auto_whatsapp_name_send(recipient: str, message: str, delay: float = 7.0):
    """
    Automates searching for a contact name on WhatsApp Web/Desktop, typing the message, and pressing Enter to send.
    """
    import threading
    def work():
        time.sleep(delay)
        try:
            import pyautogui
            print(f"[Automation] 🔍 Searching WhatsApp for contact '{recipient}'...")
            
            # 1. Focus search bar using WhatsApp shortcut (Ctrl + F)
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(0.8)
            
            # 2. Type recipient name and press Enter to select chat
            pyautogui.typewrite(recipient, interval=0.05)
            time.sleep(1.2)
            pyautogui.press('enter')
            time.sleep(1.0)
            
            # 3. Type message and press Enter to send
            safe_text = message.strip() if message else "Hello!"
            pyautogui.typewrite(safe_text, interval=0.04)
            time.sleep(0.5)
            pyautogui.press('enter')
            print(f"[Automation] 🚀 Automatically sent WhatsApp message to '{recipient}': '{safe_text}'")
        except Exception as e:
            print(f"[Automation Error] WhatsApp name auto-send failed: {e}")
            
    threading.Thread(target=work, daemon=True).start()

def send_whatsapp_message(recipient: str, message: str):
    """
    Sends a WhatsApp message automatically.
    Attempts to launch the Windows WhatsApp Desktop App via protocol, or WhatsApp Web.
    Automates sending to both saved 10-digit phone numbers and contact names!
    """
    rec = recipient.strip().lower()
    
    # Strip any leftover action prefix or junk
    rec = re.sub(r'^(to|person|contact|friend)\s+', '', rec)
    
    # Custom contact numbers lookup loaded dynamically from memory.json
    try:
        import memory_manager
        mem = memory_manager.load_memory()
        contacts = mem.get("custom_contacts", {})
    except Exception:
        contacts = {}
    
    phone = contacts.get(rec, rec)
    phone = re.sub(r'[\s\-()]', '', phone)
    safe_msg = message.strip() if message else "Hello!"
    
    if re.match(r'^\+?\d{10,15}$', phone):
        if len(phone) == 10:
            phone = "+91" + phone
        elif not phone.startswith("+"):
            phone = "+" + phone
            
        print(f"[Automation] Automating WhatsApp message to {phone}: '{safe_msg}'")
        
        try:
            encoded_msg = urllib.parse.quote(safe_msg)
            app_url = f"whatsapp://send?phone={phone}&text={encoded_msg}"
            print(f"[Automation] Launching WhatsApp Desktop App: {app_url}")
            webbrowser.open(app_url)
            auto_press_enter(4.5)
            return f"Opening WhatsApp Desktop App and sending message to {recipient}"
        except Exception:
            pass
            
        try:
            web_url = f"https://web.whatsapp.com/send?phone={phone}&text={urllib.parse.quote(safe_msg)}"
            webbrowser.open(web_url)
            auto_press_enter(12.0)
            return f"Opening WhatsApp Web and sending message to {recipient}"
        except Exception as web_ex:
            print(f"[Automation Error] WhatsApp Web fallback failed: {web_ex}")
            return "Sorry Kajal maam, I couldn't open WhatsApp."
    else:
        # If recipient is a contact name (e.g. kuldeep, sahab ji), launch WhatsApp Web and trigger GUI auto-search & send
        print(f"[Automation] Automating WhatsApp contact search for '{recipient}': '{safe_msg}'")
        webbrowser.open("https://web.whatsapp.com/")
        auto_whatsapp_name_send(recipient, safe_msg, delay=7.0)
        return f"Opening WhatsApp Web and sending message to {recipient}"

def send_instagram_message(username: str, message: str):
    """Opens Instagram Web profile or direct chat inbox."""
    user = username.strip().replace("@", "")
    if user:
        url = f"https://www.instagram.com/{user}/"
        print(f"[Automation] Opening Instagram profile of '{user}' to send: '{message}'")
        webbrowser.open(url)
        return f"Opening Instagram profile of {username}. You can write: {message}"
    else:
        url = "https://www.instagram.com/direct/inbox/"
        webbrowser.open(url)
        return "Opening Instagram Direct Messages"

def open_app(app_name: str):
    """Attempts to open a desktop app by name, or falls back to opening it as a website."""
    current_os = platform.system().lower()
    app_raw = app_name.lower().strip()
    
    # Strip leading prefixes like "jarvis open", "local", "app"
    app_clean = re.sub(r'^(jarvis|open|local|desktop|app|the)\s+', '', app_raw).strip()
    
    # 1. Keyword extraction for common apps
    if "whatsapp" in app_clean:
        if "message" in app_clean or "send" in app_clean:
            match = re.search(r'(?:to|message)\s+([a-zA-Z0-9\s]+)', app_clean)
            rec = match.group(1).strip() if match else "contact"
            return send_whatsapp_message(rec, "Hello!")
        print("[Automation] Opening WhatsApp App...")
        try:
            if current_os == "windows":
                subprocess.Popen("start whatsapp:", shell=True)
                return "Opening WhatsApp Desktop App"
        except Exception:
            pass
        return open_website("web.whatsapp.com")
        
    if any(k in app_clean for k in ["chrome", "google chrome", "googlechrome"]):
        print("[Automation] Launching Google Chrome...")
        try:
            if current_os == "windows":
                subprocess.Popen("start chrome", shell=True)
                return "Opening Google Chrome"
        except Exception:
            pass
        return open_website("google.com")
            
    if any(k in app_clean for k in ["chatgpt", "chat gpt", "gpt", "chat ppt"]):
        return open_website("chatgpt.com")

    if "instagram" in app_clean or "insta" in app_clean:
        try:
            if current_os == "windows":
                subprocess.Popen("start instagram:", shell=True)
                return "Opening Instagram App"
        except Exception:
            pass
        return open_website("instagram.com")

    if "youtube" in app_clean:
        return open_youtube()

    if "spotify" in app_clean:
        try:
            if current_os == "windows":
                subprocess.Popen("start spotify:", shell=True)
                return "Opening Spotify App"
        except Exception:
            pass
        return open_website("spotify.com")

    # Windows standard apps
    windows_apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "paint": "mspaint.exe",
        "cmd": "cmd.exe",
        "command prompt": "cmd.exe",
        "explorer": "explorer.exe",
        "file explorer": "explorer.exe",
        "folder": "explorer.exe",
        "task manager": "taskmgr.exe",
        "control panel": "control.exe",
        "code": "code",
        "vs code": "code",
        "vscode": "code",
        "visual studio code": "code"
    }
    
    try:
        if current_os == "windows":
            if app_clean in windows_apps:
                target = windows_apps[app_clean]
                subprocess.Popen(f"start {target}" if target != "code" else "code", shell=True)
                return f"Opening local application {app_clean}"
            else:
                try:
                    subprocess.Popen(f"start {app_clean}", shell=True)
                    return f"Opening local application {app_clean}"
                except Exception:
                    return open_website(app_clean)
        else:
            return open_website(app_clean)
            
    except Exception as e:
        print(f"[Automation Warning] App launch failed for '{app_clean}': {e}")
        return open_website(app_clean)

def search_google(query: str):
    """Runs a Google search for the query in the default browser."""
    print(f"[Automation] Searching Google for: '{query}'")
    safe_query = urllib.parse.quote(query.strip())
    search_url = f"https://www.google.com/search?q={safe_query}"
    webbrowser.open(search_url)
    return f"Searching Google for {query}"

def search_chatgpt(query: str):
    """Opens ChatGPT in browser and automatically types + sends the prompt query."""
    clean_query = query.strip()
    print(f"[Automation] 🤖 Searching ChatGPT for: '{clean_query}'...")
    webbrowser.open("https://chatgpt.com")
    
    import threading
    def auto_type_prompt():
        time.sleep(6.0)
        try:
            import pyautogui
            pyautogui.hotkey('shift', 'esc')
            time.sleep(0.6)
            pyautogui.typewrite(clean_query, interval=0.03)
            time.sleep(0.5)
            pyautogui.press('enter')
            print(f"[Automation] 🚀 Automatically sent prompt to ChatGPT: '{clean_query}'")
        except Exception as ex:
            print(f"[Automation Error] ChatGPT auto-prompt failed: {ex}")
            
    threading.Thread(target=auto_type_prompt, daemon=True).start()
    return f"Searching ChatGPT for {clean_query}"

def route_automation(command: str) -> str:
    """
    Parses simple single-intent commands (e.g., 'volume up', 'open whatsapp', 'lock pc').
    Returns None for complex, natural, or multi-intent commands so the AI Chatbot handles them.
    """
    cmd = command.lower().strip()
    
    # 0. Strip leading wake word if present
    cmd = re.sub(r'^(jarvis|jarvas|javas|jervis|gervis)\s+', '', cmd).strip()
    
    # 0. Reject complex multi-intent / natural sentences (pass to AI Chatbot)
    complex_indicators = [
        " and ", " send ", " message ", " search ", " karo", " karke", " usmein",
        " ko ", " se ", " par ", " batao", " bataiye", " tell me", " what is",
        " how to", " image ", " picture ", " photo ", " aur ", " to "
    ]
    if any(ind in f" {cmd} " for ind in complex_indicators):
        return None
    
    def get_num(text):
        m = re.search(r'\d+', text)
        return int(m.group()) if m else None
        
    # --- 1. Sound / Volume Controls ---
    if "volume" in cmd or "mute" in cmd or "loud" in cmd:
        num = get_num(cmd)
        if "mute" in cmd or "volume zero" in cmd or "volume 0" in cmd:
            return set_volume(0.0)
        elif "max" in cmd or "full" in cmd or "volume 100" in cmd:
            return set_volume(1.0)
        elif "up" in cmd or "increase" in cmd or "raise" in cmd:
            return change_volume(0.1)
        elif "down" in cmd or "decrease" in cmd or "lower" in cmd or "reduce" in cmd:
            return change_volume(-0.1)
        elif "high" in cmd or "loud" in cmd:
            return set_volume(0.8)
        elif "low" in cmd or "soft" in cmd:
            return set_volume(0.2)
        elif "medium" in cmd or "half" in cmd:
            return set_volume(0.5)
        elif num is not None:
            return set_volume(num / 100.0)
            
    # --- 2. Brightness Controls ---
    if "brightness" in cmd or "dim screen" in cmd or "screen light" in cmd:
        num = get_num(cmd)
        if "max" in cmd or "full" in cmd or "brightness 100" in cmd:
            return set_brightness(100)
        elif "up" in cmd or "increase" in cmd or "raise" in cmd:
            return change_brightness(10)
        elif "down" in cmd or "decrease" in cmd or "lower" in cmd or "reduce" in cmd:
            return change_brightness(-10)
        elif "low" in cmd or "dim" in cmd:
            return set_brightness(20)
        elif "medium" in cmd or "half" in cmd:
            return set_brightness(50)
        elif num is not None:
            return set_brightness(num)
            
    # --- 3. Song / YouTube Playback ---
    if "play" in cmd or "song" in cmd or "youtube" in cmd:
        if cmd != "open youtube":
            song_query = cmd
            song_query = re.sub(r'\b(play|song|music|video|on youtube|open|youtube)\b', '', song_query).strip()
            if song_query:
                return play_song(song_query)

    # --- 4. Open YouTube ---
    if "open youtube" in cmd:
        return open_youtube()
        
    # --- 5. Open Browser / Specific Websites ---
    if cmd.startswith("open "):
        target = cmd.replace("open ", "", 1).strip()
        web_keywords = ["browser", "google", "youtube"]
        if target not in web_keywords:
            return open_app(target)
        else:
            if target == "youtube":
                return open_youtube()
            return open_browser()
            
    # --- 6. Search Google ---
    if cmd.startswith("search google for ") or cmd.startswith("search for ") or cmd.startswith("google search "):
        query = cmd.replace("search google for ", "", 1).replace("search for ", "", 1).replace("google search ", "", 1).strip()
        if query:
            return search_google(query)
            
    # --- 7. Close Apps ---
    if cmd.startswith("close "):
        target = cmd.replace("close ", "", 1).strip()
        return close_app(target)
        
    # --- 8. PC Screen Lock ---
    if any(kw in cmd for kw in ["lock pc", "lock screen", "lock computer"]):
        return lock_pc()
        
    # --- 9. Screenshot Control ---
    if "screenshot" in cmd or "capture screen" in cmd:
        return take_screenshot()
             
    # --- 10. PC Power Controls ---
    if any(kw in cmd for kw in ["shutdown", "shut down", "power off", "turn off", "switch off"]):
        if "cancel" in cmd or "abort" in cmd:
            return cancel_shutdown()
        return shutdown_pc()
    
    if any(kw in cmd for kw in ["restart", "reboot"]):
        if "cancel" in cmd or "abort" in cmd:
            return cancel_shutdown()
        return restart_pc()
    
    if any(kw in cmd for kw in ["sleep", "hibernate"]):
        return sleep_pc()
    
    # --- 10.5 Run Command execution ---
    if cmd.startswith("run command ") or cmd.startswith("execute command ") or cmd.startswith("run "):
        target = command.strip().replace("run command ", "", 1).replace("execute command ", "", 1).replace("run ", "", 1).strip()
        if target:
            import subprocess
            try:
                subprocess.Popen(target, shell=True)
                return f"Running command '{target}' successfully, Boss."
            except Exception as e:
                return f"Failed to run command '{target}': {e}"

    return None

def close_app(app_name: str):
    """Closes a local application using taskkill on Windows."""
    app_clean = app_name.lower().strip()
    windows_apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "paint": "mspaint.exe",
        "cmd": "cmd.exe",
        "command prompt": "cmd.exe",
        "chrome": "chrome.exe",
        "code": "code.exe",
        "vscode": "code.exe",
        "whatsapp": "WhatsApp.exe",
        "spotify": "Spotify.exe",
    }
    
    target = windows_apps.get(app_clean, f"{app_clean}.exe")
    print(f"[Automation] Attempting to close process: {target}")
    try:
        if platform.system().lower() == "windows":
            subprocess.Popen(f"taskkill /f /im {target}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return f"Closing application {app_name}"
        else:
            return "App closing is only supported on Windows"
    except Exception as e:
        print(f"[Automation Error] Failed to close app: {e}")
        return f"Sorry Kajal maam, I couldn't close {app_name}."

def lock_pc():
    """Locks the Windows workstation."""
    try:
        if platform.system().lower() == "windows":
            subprocess.Popen("rundll32.exe user32.dll,LockWorkStation")
            return "Locking your PC"
        else:
            return "PC lock is only supported on Windows"
    except Exception as e:
        print(f"[Automation Error] Failed to lock PC: {e}")
        return "Sorry Kajal maam, I couldn't lock your PC."

def take_screenshot():
    """Takes a screenshot and saves it directly to the user's Windows Desktop."""
    try:
        import pyautogui
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        file_path = os.path.join(desktop_path, f"screenshot_{int(time.time())}.png")
        pyautogui.screenshot(file_path)
        print(f"[Automation] Screenshot saved to: {file_path}")
        return f"Screenshot taken and saved to your Desktop"
    except Exception as e:
        print(f"[Automation Error] Failed to take screenshot: {e}")
        return "Sorry Kajal maam, I couldn't capture the screen."

def shutdown_pc(delay: int = 5):
    """Shuts down the Windows PC after a brief delay."""
    print(f"[Automation] Shutting down PC in {delay} seconds...")
    try:
        subprocess.Popen(f"shutdown /s /t {delay}", shell=True)
        return f"Shutting down your PC in {delay} seconds"
    except Exception as e:
        print(f"[Automation Error] Shutdown failed: {e}")
        return "Sorry Kajal maam, I couldn't shut down the PC."

def restart_pc(delay: int = 5):
    """Restarts the Windows PC after a brief delay."""
    print(f"[Automation] Restarting PC in {delay} seconds...")
    try:
        subprocess.Popen(f"shutdown /r /t {delay}", shell=True)
        return f"Restarting your PC in {delay} seconds"
    except Exception as e:
        print(f"[Automation Error] Restart failed: {e}")
        return "Sorry Kajal maam, I couldn't restart the PC."

def sleep_pc():
    """Puts the Windows PC to sleep."""
    print("[Automation] Putting PC to sleep...")
    try:
        subprocess.Popen("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
        return "Putting your PC to sleep"
    except Exception as e:
        print(f"[Automation Error] Sleep failed: {e}")
        return "Sorry Kajal maam, I couldn't put the PC to sleep."

def logoff_pc():
    """Logs off the current Windows user."""
    print("[Automation] Logging off...")
    try:
        subprocess.Popen("shutdown /l", shell=True)
        return "Logging off your PC"
    except Exception as e:
        print(f"[Automation Error] Logoff failed: {e}")
        return "Sorry Kajal maam, I couldn't log off."

def cancel_shutdown():
    """Cancels a pending shutdown or restart."""
    print("[Automation] Cancelling scheduled shutdown/restart...")
    try:
        subprocess.Popen("shutdown /a", shell=True)
        return "Cancelled the scheduled shutdown"
    except Exception as e:
        print(f"[Automation Error] Cancel shutdown failed: {e}")
        return "Sorry Kajal maam, I couldn't cancel the shutdown."

def generate_image(prompt: str) -> str:
    """
    Generates high-quality AI images instantly using Pollinations AI (Free, 1024x1024).
    Saves the generated image to Desktop and opens it automatically.
    """
    import requests
    import urllib.parse
    clean_prompt = prompt.strip()
    print(f"[Automation] Generating AI image for prompt: '{clean_prompt}'...")
    encoded_prompt = urllib.parse.quote(clean_prompt)
    url = f"https://pollinations.ai/p/{encoded_prompt}?width=1024&height=1024&seed={int(time.time())}"
    
    try:
        res = requests.get(url, timeout=25)
        if res.status_code == 200 and len(res.content) > 1000:
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            file_name = f"ai_image_{int(time.time())}.jpg"
            file_path = os.path.join(desktop_path, file_name)
            with open(file_path, "wb") as f:
                f.write(res.content)
            print(f"[Automation] AI Image generated and saved to: {file_path}")
            webbrowser.open(file_path)
            return f"Generated AI image for {clean_prompt} and saved to your Desktop"
        else:
            print(f"[Automation Error] Pollinations AI status code: {res.status_code}")
            webbrowser.open(url)
            return f"Opening generated image for {clean_prompt} in your browser"
    except Exception as e:
        print(f"[Automation Error] Image generation failed: {e}")
        webbrowser.open(url)
        return f"Opening generated image for {clean_prompt} in your browser"

def search_wikipedia(query: str) -> str:
    """Searches Wikipedia and returns a short 2-sentence summary."""
    print(f"[Automation] Searching Wikipedia for: '{query}'")
    try:
        import wikipedia
        wikipedia.set_lang("en")
        summary = wikipedia.summary(query, sentences=2)
        print(f"[Wikipedia] Summary: {summary}")
        return summary
    except Exception as e:
        print(f"[Automation Warning] Wikipedia search failed: {e}")
        return search_google(query)

def describe_screen(chatbot=None) -> str:
    """Captures the current screen and uses Gemini / Multimodal vision to describe it."""
    try:
        import pyautogui
        import tempfile
        temp_file = tempfile.mktemp(suffix=".png")
        pyautogui.screenshot(temp_file)
        print(f"[Automation] Screen captured for vision analysis: {temp_file}")
        
        if chatbot and hasattr(chatbot, "gemini_client") and chatbot.gemini_client:
            from google.genai import types
            with open(temp_file, "rb") as f:
                img_bytes = f.read()
            response = chatbot.gemini_client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=[
                    types.Part.from_bytes(data=img_bytes, mime_type="image/png"),
                    "Describe what is currently visible on the screen concisely in 2-3 Hinglish sentences for Kajal maam."
                ]
            )
            reply = response.text.strip()
            print(f"[Vision Analysis] Jarvis: '{reply}'")
            return reply
        else:
            return "Kajal maam, I took a screenshot of your screen."
    except Exception as e:
        print(f"[Vision Error] {e}")
        return "Sorry Kajal maam, I couldn't capture and analyze the screen."

if __name__ == "__main__":
    print("--- Jarvis Automation Standalone Test ---")
