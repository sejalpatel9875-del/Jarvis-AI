import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Primary Voice Engine Settings ('sonic' or 'human')
TTS_ENGINE = os.getenv("TTS_ENGINE", "sonic").lower().strip()
HUMAN_VOICE = os.getenv("HUMAN_VOICE", "hi-IN-MadhurNeural").strip()
HINGLISH_VOICE = HUMAN_VOICE

# Cartesia Sonic Multilingual TTS Settings
CARTESIA_API_KEY = os.getenv("CARTESIA_API_KEY", os.getenv("SONIC_API_KEY", ""))
SONIC_API_KEY = CARTESIA_API_KEY
SONIC_MODEL_ID = os.getenv("SONIC_MODEL_ID", "sonic-3.5")
SONIC_VOICE_ID = os.getenv("SONIC_VOICE_ID", "db6b0ed5-d5d3-463d-ae85-518a07d3c2b4")
SONIC_LANGUAGE = os.getenv("SONIC_LANGUAGE", "hi")  # 'hi' for Hindi accent with English code-switching (Hinglish)

# Model Aliases & Defaults
CEREBRAS_ADVANCED_MODEL = os.getenv("CEREBRAS_ADVANCED_MODEL", "llama-3.3-70b")
CEREBRAS_CASUAL_MODEL = os.getenv("CEREBRAS_CASUAL_MODEL", "llama-3.1-8b")
GEMINI_ADVANCED_MODEL = os.getenv("GEMINI_ADVANCED_MODEL", "gemini-2.5-flash")
GEMINI_CASUAL_MODEL = os.getenv("GEMINI_CASUAL_MODEL", "gemini-3.1-flash-lite")

# Wake Word Settings
WAKE_WORD = os.getenv("WAKE_WORD", "jarvis").lower().strip()

# Whisper STT Model ('base' = best for 8GB RAM, fast load + fast transcription)
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")

# Ollama Local Settings
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

# Print status on startup
print("=== Jarvis Configuration Loaded ===")
print(f"Voice Engine:     {TTS_ENGINE.upper()}")
if TTS_ENGINE == "sonic":
    print(f"Sonic Model:      {SONIC_MODEL_ID} (Language: {SONIC_LANGUAGE})")
    print(f"Sonic API Key:    {'Yes' if CARTESIA_API_KEY else 'No'}")
else:
    print(f"Primary Voice:    Microsoft Neural Human Voice ({HUMAN_VOICE})")
print(f"Groq API Key:     {'Yes' if GROQ_API_KEY else 'No'}")
print(f"Gemini API Key:   {'Yes' if GEMINI_API_KEY and GEMINI_API_KEY != 'your_gemini_api_key_here' else 'No'}")
print(f"Ollama Model:     {OLLAMA_MODEL} (Local)")
print(f"AI Sequence:      1. Groq  ->  2. Gemini  ->  3. Ollama")
print(f"Wake Word:        {WAKE_WORD}")
print(f"Whisper STT:      {WHISPER_MODEL} (CPU + INT8)")
print("===================================")
