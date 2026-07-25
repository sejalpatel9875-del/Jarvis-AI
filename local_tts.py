import os
import sys
import warnings
import asyncio
import tempfile
import re
import urllib.request
import sounddevice as sd
import soundfile as sf
import edge_tts
import config

# Suppress harmless PyTorch and HuggingFace warnings for clean terminal output
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Reconfigure stdout/stderr to support printing UTF-8 characters on Windows command prompt
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

# Add eSpeak NG to environment PATH so Kokoro can find espeak-ng.dll and run phonemizers
espeak_path = r"C:\Program Files\eSpeak NG"
if espeak_path not in os.environ["PATH"]:
    os.environ["PATH"] += os.pathsep + espeak_path

# Global pipeline variable for Kokoro fallback
pipeline = None

def get_pipeline():
    """Lazily load the Kokoro pipeline only when needed to save startup memory."""
    global pipeline
    if pipeline is None:
        try:
            from kokoro import KPipeline
            voice_lang = getattr(config, "KOKORO_VOICE_LANG", "a") # 'a' for American English
            print(f"[Local TTS] Loading Kokoro Pipeline for language: {voice_lang}...")
            pipeline = KPipeline(lang_code=voice_lang, repo_id='hexgrad/Kokoro-82M')
            print("[Local TTS] Kokoro model loaded successfully.")
        except Exception as e:
            print(f"[Local TTS Error] Failed to load Kokoro Pipeline: {e}")
    return pipeline

def detect_voice_for_text(text: str) -> str:
    """
    Detects if the text contains Devanagari characters or common Hindi/Hinglish structural words
    and returns 'hi-IN-MadhurNeural' (Hindi voice) or fallback to config.TTS_VOICE (English voice).
    """
    if any(ord(char) in range(0x0900, 0x0980) for char in text):
        return "hi-IN-MadhurNeural"
        
    hinglish_keywords = {
        "hai", "kya", "haan", "aap", "nhi", "nahi", "ho", "ka", "se", "ko", 
        "rha", "raha", "rhi", "rahi", "hu", "hoon", "bataiye", "karna", "krna", 
        "bolu", "kar", "dena", "maam", "aavaj", "aa", "rahi", "aaya", "aayi", "gaya"
    }
    
    words = re.findall(r'\b[a-z]+\b', text.lower())
    if any(w in hinglish_keywords for w in words):
        return "hi-IN-MadhurNeural"
        
    return config.TTS_VOICE

def is_online() -> bool:
    """Checks if internet connection is active."""
    try:
        urllib.request.urlopen("https://www.google.com", timeout=1.5)
        return True
    except Exception:
        return False

async def speak_edge_tts_async(text: str, voice: str):
    """Generates and plays TTS using Microsoft Edge TTS (0 rate limit, free, online)."""
    temp_fd, temp_path = tempfile.mkstemp(suffix=".mp3")
    os.close(temp_fd)
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(temp_path)
        data, fs = sf.read(temp_path)
        sd.play(data, fs)
        sd.wait()
    finally:
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception:
            pass

def speak(text: str, voice: str = None):
    """
    Speaks the text. Dynamically uses Edge TTS (for high-quality Hindi/English switching)
    if online, otherwise falls back to local Kokoro TTS (fully offline).
    """
    cleaned_text = re.sub(r'\[ACTION:\s*\w+\s*\|\s*.*?\]', '', text).strip()
    if not cleaned_text:
        return
        
    print(f"[Local TTS] Jarvis: '{cleaned_text}'")
    
    # 1. Try Premium Edge TTS (online, free, 0 limits)
    if is_online():
        if not voice:
            voice = detect_voice_for_text(cleaned_text)
        try:
            asyncio.run(speak_edge_tts_async(cleaned_text, voice))
            return
        except Exception as e:
            print(f"[Local TTS Warning] Edge TTS failed: {e}. Falling back to Kokoro.")
            
    # 2. Offline Fallback to Local Kokoro TTS
    pipe = get_pipeline()
    if not pipe:
        print("[Local TTS Error] Offline Kokoro is not available. Speech skipped.")
        return
        
    try:
        kokoro_voice = getattr(config, "KOKORO_VOICE", "af_heart")
        generator = pipe(cleaned_text, voice=kokoro_voice, speed=1.0)
        for gs, ps, audio in generator:
            if audio is not None and len(audio) > 0:
                sd.play(audio, 24000)
                sd.wait()
    except Exception as e:
        print(f"[Local TTS Playback Error] {e}")

if __name__ == "__main__":
    print("--- Jarvis Local TTS Standalone Test ---")
    speak("Hello Kajal maam, local Kokoro and online Edge hybrid TTS is now active.")
    speak("हाँ काजल मैम, आपकी आवाज़ बिल्कुल साफ आ रही है।")
