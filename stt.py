import io
import sys
import time
import socket
import re
import numpy as np
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
import config
from collections import deque
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError

# Reconfigure stdout/stderr to support printing UTF-8 characters on Windows
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Set global socket timeout to 6.0 seconds to allow natural network requests without premature truncation
socket.setdefaulttimeout(6.0)

# Dedicated thread pool for non-blocking transcription
_executor = ThreadPoolExecutor(max_workers=2)

# ============================================================
# Ultra-Fast Adaptive STT Engine (Zero Freeze, Zero Delay VAD)
# - Phonetic Normalization: Maps "4g pt" / "4g ppt" -> "chatgpt"
# - Dual Language: Tries English (en-IN) and Hindi (hi-IN)
# - Dynamic VAD: Automatically detects end of sentence in <0.9s
# ============================================================

def clean_speech_text(text: str) -> str:
    """Corrects common Indian English STT misrecognitions phonetically."""
    if not text:
        return ""
    cleaned = text.strip().lower()
    
    # Fix ChatGPT phonetics misheard as 4G, 4G PPT, Chat PPT, etc.
    gpt_patterns = [
        (r'\b4g\s*ppt\b', 'chatgpt'),
        (r'\b4g\s*pt\b', 'chatgpt'),
        (r'\b4g\s*app\b', 'chatgpt'),
        (r'\b4g\s*p\b', 'chatgpt'),
        (r'\b4g\b', 'chatgpt'),
        (r'\bchat\s*ppt\b', 'chatgpt'),
        (r'\bcat\s*gpt\b', 'chatgpt'),
        (r'\bchar\s*gpt\b', 'chatgpt'),
        (r'\bchachi\s*pt\b', 'chatgpt'),
        (r'\bchachi\s*bt\b', 'chatgpt'),
    ]
    for pattern, replacement in gpt_patterns:
        cleaned = re.sub(pattern, replacement, cleaned)
        
    return cleaned

def _recognize_google_worker(audio_data, language="en-IN"):
    """Worker function executed inside thread pool."""
    recognizer = sr.Recognizer()
    try:
        text = recognizer.recognize_google(audio_data, language=language)
        if text and text.strip():
            return clean_speech_text(text)
    except Exception:
        pass
        
    try:
        if language != "hi-IN":
            text_hi = recognizer.recognize_google(audio_data, language="hi-IN")
            if text_hi and text_hi.strip():
                return clean_speech_text(text_hi)
    except Exception:
        pass
        
    return None

def transcribe_audio(audio_np: np.ndarray, samplerate: int = 16000) -> str:
    """
    Transcribes audio with a 5.0s timeout.
    Guaranteed NEVER to freeze or hang the assistant.
    """
    try:
        wav_io = io.BytesIO()
        sf.write(wav_io, audio_np, samplerate, format='WAV', subtype='PCM_16')
        wav_io.seek(0)
        
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_io) as source:
            audio_data = recognizer.record(source)
        
        # Submit to thread pool with 5.0s hard timeout
        future = _executor.submit(_recognize_google_worker, audio_data, "en-IN")
        result = future.result(timeout=5.0)
        return result
    except FutureTimeoutError:
        print("[STT Warning] Transcription network timeout (>5.0s). Resuming listening.")
        return None
    except Exception as e:
        print(f"[STT Error] {e}")
        return None

def _compute_audio_energy(audio_np: np.ndarray) -> float:
    """Compute RMS energy of audio array."""
    audio_float = audio_np.flatten().astype(float)
    return float(np.sqrt(np.mean(audio_float**2)))

def listen(timeout=8, phrase_time_limit=12, calibration_duration=0.4, engine="google"):
    """
    Captures mic audio with dynamic adaptive Voice Activity Detection (VAD).
    Detects end of sentence instantly within 0.9 seconds of silence.
    """
    samplerate = 16000
    channels = 1
    chunk_size = 1024
    
    print("\n[STT] Calibrating...")
    
    try:
        calibration_frames = int(calibration_duration * samplerate)
        ambient_audio = sd.rec(calibration_frames, samplerate=samplerate, channels=channels, dtype='int16')
        sd.wait()
        
        window_size = 1600  # 100ms windows
        rms_values = []
        audio_flat = ambient_audio.flatten().astype(float)
        for i in range(0, len(audio_flat) - window_size, window_size):
            window = audio_flat[i:i + window_size]
            rms_values.append(np.sqrt(np.mean(window**2)))
        
        if rms_values:
            ambient_rms = float(np.median(rms_values))
        else:
            ambient_rms = np.sqrt(np.mean(audio_flat**2))
        
        # Sensitive threshold: 1.25x ambient noise floor + 15 offset (low floor of 45 for soft speech)
        threshold = max(ambient_rms * 1.25 + 15.0, 45.0)
        print(f"[STT] Noise Floor: {ambient_rms:.0f} | Dynamic Threshold: {threshold:.0f}")
        
    except Exception as e:
        print(f"[STT Warning] Calibration failed: {e}")
        threshold = 60.0

    print("[STT] 🎤 Listening...")
    
    recorded_chunks = []
    speaking = False
    silence_start = None
    start_time = time.time()
    speech_start_time = None
    consecutive_speech_chunks = 0
    max_speech_rms = threshold
    
    pre_buffer_size = max(int(0.3 * samplerate / chunk_size), 5)
    pre_buffer = deque(maxlen=pre_buffer_size)
    
    SILENCE_TO_STOP = 0.9  # Stops recording 0.9s after user finishes speaking
    MIN_SPEECH_CHUNKS = 2
    
    try:
        with sd.InputStream(samplerate=samplerate, channels=channels, dtype='int16', blocksize=chunk_size) as stream:
            while True:
                chunk, overflowed = stream.read(chunk_size)
                rms = np.sqrt(np.mean(chunk.astype(float)**2))
                curr_time = time.time()
                
                if not speaking:
                    pre_buffer.append(chunk.copy())
                    
                    if rms > threshold:
                        consecutive_speech_chunks += 1
                        if consecutive_speech_chunks >= MIN_SPEECH_CHUNKS:
                            print("[STT] 🗣️ Speech detected, recording...")
                            speaking = True
                            speech_start_time = curr_time
                            max_speech_rms = rms
                            for buffered_chunk in pre_buffer:
                                recorded_chunks.append(buffered_chunk)
                            pre_buffer.clear()
                    else:
                        consecutive_speech_chunks = 0
                    
                    if curr_time - start_time > timeout:
                        print("[STT] Timed out.")
                        return None
                else:
                    recorded_chunks.append(chunk)
                    if rms > max_speech_rms:
                        max_speech_rms = rms
                    
                    if curr_time - speech_start_time > phrase_time_limit:
                        print("[STT] Max recording duration reached.")
                        break
                    
                    # Silence detection: consider silent if RMS drops below 40% of speech peak or baseline threshold
                    silence_cutoff = max(threshold, max_speech_rms * 0.4)
                    
                    if rms >= silence_cutoff:
                        silence_start = None  # Reset silence timer while user is speaking
                    else:
                        if silence_start is None:
                            silence_start = curr_time
                        elif curr_time - silence_start > SILENCE_TO_STOP:
                            print("[STT] ✅ Sentence complete (silence detected).")
                            break
                            
                time.sleep(0.005)
                
    except Exception as e:
        print(f"[STT Error] Mic failed: {e}")
        return None

    if not recorded_chunks:
        return None
    
    audio_data = np.concatenate(recorded_chunks, axis=0)
    audio_energy = _compute_audio_energy(audio_data)
    min_energy = threshold * 0.35
    audio_duration = len(audio_data) / samplerate
    
    if audio_energy < min_energy or audio_duration < 0.3:
        print(f"[STT] Rejected: low energy ({audio_energy:.0f}) or too short ({audio_duration:.1f}s)")
        return None
    
    print(f"[STT] 🧠 Transcribing ({audio_duration:.1f}s audio)...")
    start_t = time.time()
    text = transcribe_audio(audio_data, samplerate)
    elapsed = time.time() - start_t
    
    if text:
        cleaned_text = clean_speech_text(text)
        print(f"[STT] 🎯 Result ({elapsed:.2f}s): '{cleaned_text}'")
        return cleaned_text
    else:
        print(f"[STT] No speech recognized ({elapsed:.2f}s).")
        return None

if __name__ == "__main__":
    print("--- Bulletproof Adaptive STT Test ---")
    print("Speak naturally. Press Ctrl+C to exit.\n")
    
    try:
        while True:
            text = listen()
            if text:
                print(f">> Heard: '{text}'")
            print("-" * 50)
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nExiting STT test.")
