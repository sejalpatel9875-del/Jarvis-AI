import io
import time
import sys
import numpy as np
import sounddevice as sd
import soundfile as sf
import config

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

# Global model variable to save RAM by loading only once
whisper_model = None

def get_whisper_model():
    """Lazily loads the Whisper model to save memory during startup."""
    global whisper_model
    if whisper_model is None:
        try:
            from faster_whisper import WhisperModel
            model_size = getattr(config, "WHISPER_MODEL", "base")
            print(f"[Local STT] Loading Whisper model size: {model_size} on CPU (int8)...")
            # Using CPU and int8 for memory efficiency on 8GB RAM machines
            whisper_model = WhisperModel(model_size, device="cpu", compute_type="int8")
            print("[Local STT] Whisper model loaded successfully.")
        except Exception as e:
            print(f"[Local STT Error] Failed to load Whisper model: {e}")
    return whisper_model

def transcribe_audio(wav_data_io) -> str:
    """
    Transcribes audio from a WAV file-like object using faster-whisper.
    """
    model = get_whisper_model()
    if not model:
        print("[Local STT Error] Whisper model is not loaded.")
        return None
        
    try:
        # Transcribe WAV bytes
        segments, info = model.transcribe(wav_data_io, beam_size=5, vad_filter=True)
        
        # Combine segments into single string
        text_segments = [segment.text for segment in segments]
        text = " ".join(text_segments).strip()
        return text if text else None
    except Exception as e:
        print(f"[Local STT Error] Transcription failed: {e}")
        return None

def listen(timeout=5, phrase_time_limit=10, calibration_duration=1.0) -> str:
    """
    Captures mic audio using sounddevice, performs local RMS-based VAD,
    and decodes speech offline using faster-whisper.
    """
    samplerate = 16000
    channels = 1
    chunk_size = 1024
    
    print("\n[Local STT] Calibrating ambient noise... (Please be quiet)")
    
    try:
        calibration_frames = int(calibration_duration * samplerate)
        ambient_audio = sd.rec(calibration_frames, samplerate=samplerate, channels=channels, dtype='int16')
        sd.wait()
        ambient_rms = np.sqrt(np.mean(ambient_audio.astype(float)**2))
        threshold = max(ambient_rms * 1.5, 150.0)
        print(f"[Local STT] Dynamic Threshold: {threshold:.2f} (Noise floor: {ambient_rms:.2f})")
    except Exception as e:
        print(f"[Local STT Warning] Calibration failed: {e}. Using default threshold.")
        threshold = 200.0

    print("[Local STT] Offline listening started...")
    
    recorded_chunks = []
    speaking = False
    silence_start = None
    start_time = time.time()
    speech_start_time = None
    
    try:
        with sd.InputStream(samplerate=samplerate, channels=channels, dtype='int16', blocksize=chunk_size) as stream:
            while True:
                chunk, overflowed = stream.read(chunk_size)
                rms = np.sqrt(np.mean(chunk.astype(float)**2))
                curr_time = time.time()
                
                if not speaking:
                    if rms > threshold:
                        print("[Local STT] User speaking...")
                        speaking = True
                        speech_start_time = curr_time
                        recorded_chunks.append(chunk)
                    else:
                        if curr_time - start_time > timeout:
                            print("[Local STT] Timeout. No speech detected.")
                            return None
                else:
                    recorded_chunks.append(chunk)
                    
                    if curr_time - speech_start_time > phrase_time_limit:
                        print("[Local STT] Reached maximum speech limit.")
                        break
                        
                    if rms > threshold:
                        silence_start = None
                    else:
                        if silence_start is None:
                            silence_start = curr_time
                        elif curr_time - silence_start > 1.2:
                            print("[Local STT] Audio captured.")
                            break
                            
                time.sleep(0.01)
                
    except Exception as e:
        print(f"[Local STT Error] Mic capture failed: {e}")
        return None

    if not recorded_chunks:
        return None
        
    # Build in-memory WAV
    audio_data = np.concatenate(recorded_chunks, axis=0)
    wav_io = io.BytesIO()
    sf.write(wav_io, audio_data, samplerate, format='WAV', subtype='PCM_16')
    wav_io.seek(0)
    
    print("[Local STT] Transcribing speech offline...")
    text = transcribe_audio(wav_io)
    
    if text:
        cleaned = text.strip().lower()
        print(f"[Local STT] Result: '{cleaned}'")
        return cleaned
    return None

if __name__ == "__main__":
    print("--- Jarvis Local STT Standalone Test ---")
    while True:
        try:
            res = listen()
            if res:
                print(f"You said: {res}")
        except KeyboardInterrupt:
            break
