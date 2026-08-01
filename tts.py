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

def detect_language(text: str) -> str:
    """
    Detects if language is Hindi (Devanagari), Hinglish (Roman Hindi), or English.
    Supports only these three languages.
    """
    if re.search(r"[\u0900-\u097F]", text):
        return "hindi"
    
    # Common Hinglish Roman Hindi markers
    hinglish_words = r"\b(kya|hai|hain|mujhe|mera|meri|aap|tum|kar|karo|batao|kaise|nahi|nahin|kyun|sab|badhiya|haan|achha|accha|hum|humne|humko|ji|bhaiya|yaar|ho|haye|bhaya|amigo)\b"
    if re.search(hinglish_words, text.lower()):
        return "hinglish"
    
    return "english"

def select_human_voice(lang: str = "hinglish") -> str:
    """Selects the human neural voice for speech synthesis based on detected language."""
    if lang == "english":
        return "en-IN-NeerjaNeural"
    return getattr(config, "HUMAN_VOICE", "hi-IN-MadhurNeural")

def apply_prayagraj_tone(text: str, lang: str) -> str:
    """
    Transforms text to match a friendly, natural UP Prayagraj conversational tone.
    Uses first person plural 'hum' instead of 'main', adds colloquial expressions,
    and removes stiff formal/robotic wording.
    """
    if lang == "english":
        return text

    # Apply Roman Hinglish Prayagraj mappings
    if lang == "hinglish":
        t = text
        
        # Replace singular first person pronouns with Eastern UP plural "hum"
        t = re.sub(r"\bmain\b", "hum", t, flags=re.IGNORECASE)
        t = re.sub(r"\bmujhe\b", "humko", t, flags=re.IGNORECASE)
        t = re.sub(r"\bmera\b", "humar", t, flags=re.IGNORECASE)
        t = re.sub(r"\bmere\b", "humar", t, flags=re.IGNORECASE)
        t = re.sub(r"\bmeri\b", "humaar", t, flags=re.IGNORECASE)
        
        # Add conversational flavor
        if not re.search(r"\b(bhaiya|boss|yaar|ji|amigo)\b", t.lower()):
            t = "Arey bhaiya, " + t
            
        replacements = [
            (r"\btheek hai\b", "thik hai bhaiya"),
            (r"\bkaise ho\b", "kaise ho yaar, sab badhiya?"),
            (r"\bkarta hoon\b", "karte hain"),
            (r"\bkarti hoon\b", "karte hain"),
            (r"\bkarta hu\b", "karte hain"),
            (r"\bkarunga\b", "kar denge"),
            (r"\bkarungi\b", "kar denge"),
            (r"\bbol raha hoon\b", "bol rahe hain"),
            (r"\bbata raha hoon\b", "bata rahe hain"),
            (r"\bapna\b", "apna bilkul"),
            (r"\bho gaya\b", "ho gaya bhaiya"),
            (r"\bho gaya hai\b", "ho gaya hai bhaiya"),
            (r"\bkar diya\b", "kar diye hain"),
            (r"\bde diya\b", "de diye hain"),
            (r"\ble liya\b", "le liye hain"),
        ]
        for pattern, repl in replacements:
            t = re.sub(pattern, repl, t, flags=re.IGNORECASE)
        return t

    # Apply Devanagari Hindi Prayagraj mappings
    if lang == "hindi":
        t = text
        
        # Replace pronouns: "मैं" -> "हम", "मुझे" -> "हमको", "मेरा" -> "हमार"
        t = re.sub(r"\bमैं\b", "हम", t)
        t = re.sub(r"\bमुझे\b", "हमको", t)
        t = re.sub(r"\bमेरा\b", "हमार", t)
        t = re.sub(r"\bमेरे\b", "हमार", t)
        t = re.sub(r"\bमेरी\b", "हमार", t)

        # Add conversational flavor
        if "भैया" not in t and "बॉस" not in t and "यार" not in t:
            t = "अरे भैया, " + t
            
        replacements = [
            (r"\bठीक है\b", "ठीक है भैया"),
            (r"\bकैसे हो\b", "कैसे हो यार, सब बढ़िया?"),
            (r"\bकरता हूँ\b", "करते हैं"),
            (r"\bकरती हूँ\b", "करते हैं"),
            (r"\bकरूँगा\b", "कर देंगे"),
            (r"\bकरूँगी\b", "कर देंगे"),
            (r"\bबोल रहा हूँ\b", "बोल रहे हैं"),
            (r"\bबता रहा हूँ\b", "बता रहे हैं"),
            (r"\bहो गया\b", "हो गया भैया"),
            (r"\bकर दिया\b", "कर दिए हैं"),
            (r"\bदे दिया\b", "दे दिए हैं"),
            (r"\bले लिया\b", "ले लिए हैं"),
        ]
        for pattern, repl in replacements:
            t = re.sub(pattern, repl, t)
        return t

    return text

def optimize_tts_punctuation(text: str, lang: str) -> str:
    """
    Improves pronunciation of acronyms, normalizes abbreviations,
    and inserts strategic commas to dictate natural human pauses.
    """
    t = text
    
    # Remove repeated words
    t = re.sub(r'\b(\w+)\s+\1\b', r'\1', t, flags=re.IGNORECASE)
    
    # Improve acronyms and technical terms pronunciation
    if lang == "english":
        acronyms = [
            (r"\bAI\b", "ay-eye"),
            (r"\bOS\b", "oh-es"),
            (r"\bVS\b", "vess-us"),
            (r"\bAPI\b", "ay-pee-eye"),
            (r"\bGUI\b", "jee-you-eye"),
            (r"\bTTS\b", "tee-tee-es"),
            (r"\bSTT\b", "es-tee-tee"),
            (r"\bUI\b", "you-eye"),
            (r"\bPDF\b", "pee-dee-ef"),
            (r"\bCRM\b", "see-ar-em"),
        ]
        for pattern, repl in acronyms:
            t = re.sub(pattern, repl, t)
            
    elif lang in ["hindi", "hinglish"]:
        acronyms = [
            (r"\bAI\b", "aai-aai"),
            (r"\bOS\b", "oh-es"),
            (r"\bAPI\b", "aai-pee-aai"),
            (r"\bUI\b", "you-aai"),
            (r"\bPDF\b", "pee-dee-ef"),
            (r"\bCRM\b", "see-ar-em"),
        ]
        for pattern, repl in acronyms:
            t = re.sub(pattern, repl, t)

    # Convert numbers to spoken word forms
    if lang == "english":
        t = re.sub(r'\b15%\b', 'fifteen percent', t)
        t = re.sub(r'\b100%\b', 'one hundred percent', t)
    else:
        t = re.sub(r'\b15%\b', 'pandrah percent', t)
        t = re.sub(r'\b100%\b', 'sau percent', t)

    # Insert punctuation commas before conjunctions to force natural pauses
    conjunctions_en = r"\b(but|because|and|so|then|which)\b"
    conjunctions_hi = r"\b(aur|lekin|kyunki|par|to|fir)\b"
    
    if lang == "english":
        t = re.sub(conjunctions_en, r', \1', t, flags=re.IGNORECASE)
    else:
        t = re.sub(conjunctions_hi, r', \1', t, flags=re.IGNORECASE)
        
    # Clean up double commas
    t = re.sub(r',\s*,', ',', t)
    
    # Avoid stiff robotic phrases
    robotic_phrases = [
        (r"system initialized", "system start ho gaya hai bhaiya"),
        (r"i am ready to receive commands", "hum bilkul tayyar hain, bataiye kya karna hai"),
        (r"processing your request", "ek second rukiye, hum abhi dekh rahe hain"),
        (r"operation completed successfully", "kaam ho gaya hai bhaiya"),
        (r"how can i help you", "bataiye bhaiya, kya madad chahiye?"),
    ]
    for pattern, repl in robotic_phrases:
        t = re.sub(pattern, repl, t, flags=re.IGNORECASE)
        
    return t.strip()

async def speak_human_neural_async(text: str, voice: str = None):
    """
    Synthesizes speech using Microsoft Studio Human Neural Voice at natural human speech rate (+15%).
    Produces crystal clear, natural human speech with perfect Hindi + English (Hinglish) pronunciation.
    """
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

def speak_gtts_fallback(text: str, lang: str = "hi") -> bool:
    """Fallback speech generation using gTTS."""
    temp_path = tempfile.mktemp(suffix=".mp3")
    try:
        gtts_lang = "en" if lang == "english" else "hi"
        tts = gTTS(text=text, lang=gtts_lang)
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
    Speaks text in ultra-clear, natural human speech with UP Prayagraj flavor.
    Optimizes performance by segmenting into short sentences for immediate playback.
    """
    cleaned_text = clean_for_speech(text)
    if not cleaned_text or cleaned_text.startswith("Response:"):
        return
        
    lang = detect_language(cleaned_text)
    toned_text = apply_prayagraj_tone(cleaned_text, lang)
    optimized_text = optimize_tts_punctuation(toned_text, lang)
    
    print(f"[TTS Voice Engine] Jarvis ({lang.upper()}): '{optimized_text}'")
    
    if not voice:
        voice = select_human_voice(lang)
        
    tts_engine = getattr(config, "TTS_ENGINE", "human")
    
    # Split text into sentences for instant playback streaming/pipelining
    sentences = [s.strip() for s in re.split(r'[.!?।\n]', optimized_text) if s.strip()]
    if not sentences:
        return

    for sentence in sentences:
        # Cartesia Sonic Multilingual TTS
        if tts_engine == "sonic":
            if speak_sonic(sentence):
                continue
                
        # Primary Studio Neural Human Voice
        try:
            success = asyncio.run(speak_human_neural_async(sentence, voice))
            if success:
                continue
        except Exception as ex:
            print(f"[TTS Error] Primary human voice failed: {ex}")

        # gTTS Fallback
        speak_gtts_fallback(sentence, lang)

if __name__ == "__main__":
    print("--- Jarvis UP Prayagraj Voice Test ---")
    speak("Namaste Boss! Hum aapke saare kaam dekh rahe hain. Aap bilkul chinta mat kariyo.")
