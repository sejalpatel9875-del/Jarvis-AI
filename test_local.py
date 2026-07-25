import os
import sys
import time

# Verify Python 3.12 environment is loaded
print(f"Python Version: {sys.version}")
print(f"Current Working Directory: {os.getcwd()}")
print("=" * 50)

try:
    print("[1/3] Testing Local LLM Chatbot (Ollama/Gemma3)...")
    import local_llm
    bot = local_llm.LocalChatbot()
    reply = bot.ask("Hello, who are you? Reply in one sentence.")
    print(f"LLM Reply: {reply}")
    print("Local LLM Chatbot test: SUCCESS\n")
except Exception as e:
    print(f"Local LLM Chatbot test: FAILED - {e}\n")

try:
    print("[2/3] Testing Local TTS (Kokoro)...")
    import local_tts
    # Initialize pipeline
    pipe = local_tts.get_pipeline()
    if pipe:
        print("Kokoro model loaded successfully!")
        print("Speaking test message...")
        local_tts.speak("Hello Kajal maam, local speech synthesis is working.")
        print("Local TTS test: SUCCESS\n")
    else:
        print("Local TTS test: FAILED - Kokoro pipeline not initialized\n")
except Exception as e:
    print(f"Local TTS test: FAILED - {e}\n")

try:
    print("[3/3] Testing Local STT (faster-whisper)...")
    import local_stt
    model = local_stt.get_whisper_model()
    if model:
        print("Whisper model loaded successfully!")
        print("Local STT test: SUCCESS\n")
    else:
        print("Local STT test: FAILED - Whisper model not loaded\n")
except Exception as e:
    print(f"Local STT test: FAILED - {e}\n")

print("=" * 50)
print("Local AI Stack Diagnostic Completed.")
