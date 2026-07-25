import os
import sys
import time
import tempfile
import asyncio
import re
import io
import requests
import sounddevice as sd
import soundfile as sf
import edge_tts
from gtts import gTTS
import config

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

def select_human_voice() -> str:
    """Selects the human neural voice for speech synthesis (hi-IN-MadhurNeural / hi-IN-SwaraNeural)."""
    return getattr(config, "HUMAN_VOICE", "hi-IN-MadhurNeural")

async def speak_human_neural_async(text: str, voice: str = None):
    """
    Synthesizes speech using Microsoft Studio Human Neural Voice at natural human speech rate (+15%).
    Produces crystal clear, natural human speech with perfect Hindi + English (Hinglish) pronunciation.
    """
    if not voice:
        voice = select_human_voice()
        
    temp_fd, temp_path = tempfile.mkstemp(suffix=".mp3")
    os.close(temp_fd)
    try:
        communicate = edge_tts.Communicate(text, voice, rate="+15%")
        await communicate.save(temp_path)
        data, fs = sf.read(temp_path)
        sd.play(data, fs)
        sd.wait()
        return True
    except Exception as e:
        print(f"[Human Neural Voice Error] Edge TTS failed: {e}")
        return False
    finally:
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception:
            pass

def speak_sonic(text: str) -> bool:
    """
    Synthesizes speech using Cartesia Sonic Multilingual TTS API.
    Sends "language": "hi" to render speech in natural Hindi accent with English code-switching (Hinglish).
    Endpoint: https://api.cartesia.ai/tts/bytes
    """
    api_key = getattr(config, "CARTESIA_API_KEY", "") or getattr(config, "SONIC_API_KEY", "")
    if not api_key:
        return False
        
    url = "https://api.cartesia.ai/tts/bytes"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Cartesia-Version": "2026-03-01",
        "Content-Type": "application/json"
    }
    model_id = getattr(config, "SONIC_MODEL_ID", "sonic-3.5")
    voice_id = getattr(config, "SONIC_VOICE_ID", "db6b0ed5-d5d3-463d-ae85-518a07d3c2b4")
    language = getattr(config, "SONIC_LANGUAGE", "hi")
    
    payload = {
        "model_id": model_id,
        "transcript": text,
        "voice": {
            "mode": "id",
            "id": voice_id
        },
        "language": language,
        "output_format": {
            "container": "wav",
            "encoding": "pcm_s16le",
            "sample_rate": 44100
        }
    }
    
    try:
        print(f"[Sonic Multilingual TTS API] Requesting speech via Cartesia ({model_id}, Language: '{language}')...")
        start_t = time.time()
        res = requests.post(url, headers=headers, json=payload, timeout=3.0)
        elapsed = time.time() - start_t
        
        if res.status_code == 200 and len(res.content) > 500:
            print(f"[Sonic TTS ({elapsed:.2f}s)] Playing audio response...")
            audio_data, fs = sf.read(io.BytesIO(res.content))
            sd.play(audio_data, fs)
            sd.wait()
            return True
        else:
            print(f"[Sonic TTS Warning {res.status_code}] Falling back to Microsoft Neural Human Voice...")
            return False
    except Exception as e:
        print(f"[Sonic TTS Exception] {e}. Falling back to Microsoft Neural Human Voice...")
        return False

def speak_gtts_fallback(text: str) -> bool:
    """Fallback speech generation using gTTS."""
    temp_path = tempfile.mktemp(suffix=".mp3")
    try:
        tts = gTTS(text=text, lang="hi")
        tts.save(temp_path)
        data, fs = sf.read(temp_path)
        faster_fs = int(fs * 1.2)
        sd.play(data, faster_fs)
        sd.wait()
        return True
    except Exception as e:
        print(f"[gTTS Warning] gTTS fallback failed: {e}")
        return False
    finally:
        try:
            if os.path.exists(temp_path):
                os.remove(temp_path)
        except Exception:
            pass

def clean_for_speech(text: str) -> str:
    """Sanitizes output text so TTS speaks only clean natural sentences."""
    if not text:
        return ""
    # Strip action tags
    t = re.sub(r'\[ACTION:.*?\]', '', text)
    # Strip markdown code blocks ``` ... ```
    t = re.sub(r'```.*?```', '', t, flags=re.DOTALL)
    # Strip dictionary formatting like Response: "..." Actions: [...]
    t = re.sub(r"Response:\s*[\"'](.*?)[\"']\s*Actions:.*", r"\1", t, flags=re.DOTALL)
    # Strip raw URLs
    t = re.sub(r'https?://\S+', '', t)
    return t.strip()

def speak(text: str, voice: str = None):
    """
    Primary TTS entry point for Jarvis.
    Speaks text in ultra-clear, natural human speech.
    """
    cleaned_text = clean_for_speech(text)
    if not cleaned_text or cleaned_text.startswith("Response:"):
        return
        
    print(f"[TTS Voice Engine] Jarvis: '{cleaned_text}'")
    
    tts_engine = getattr(config, "TTS_ENGINE", "human")
    
    # 1. Option A: Cartesia Sonic Multilingual TTS if explicitly selected
    if tts_engine == "sonic":
        if speak_sonic(cleaned_text):
            return
            
    # 2. Option B: Primary Studio Neural Human Voice (hi-IN-MadhurNeural / hi-IN-SwaraNeural)
    try:
        success = asyncio.run(speak_human_neural_async(cleaned_text, voice))
        if success:
            return
    except Exception as ex:
        print(f"[TTS Error] Primary human voice failed: {ex}")

    # 3. Option C: gTTS Fallback
    speak_gtts_fallback(cleaned_text)

if __name__ == "__main__":
    print("--- Jarvis Multilingual Voice Test ---")
    speak("Namaste Boss! Main aapka Jarvis hoon.")
