import asyncio
import sys
import queue
import threading
import numpy as np
import sounddevice as sd
from google import genai
from google.genai import types
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

# Queues for passing audio chunks between threads/async tasks
playback_queue = queue.Queue()
input_queue = asyncio.Queue()

# Thread-safe flag indicating if Jarvis is currently speaking (playing audio)
is_playing = False

# Event to stop the playback thread
stop_playback_event = threading.Event()

def playback_worker():
    """
    Worker thread that reads raw audio chunks from playback_queue and
    writes them to a sounddevice OutputStream. This avoids blocking
    the main asyncio event loop during audio rendering.
    """
    global is_playing
    
    # Gemini Live output is raw 16-bit PCM at 24kHz, mono, little-endian
    samplerate = 24000
    channels = 1
    
    print("[Realtime Player] Playback worker thread started.")
    
    try:
        with sd.OutputStream(samplerate=samplerate, channels=channels, dtype='int16') as stream:
            while not stop_playback_event.is_set():
                try:
                    # Non-blocking get with timeout to allow checking stop event
                    data = playback_queue.get(timeout=0.1)
                    if data is None:
                        is_playing = False
                        playback_queue.task_done()
                        break
                    
                    # Convert raw bytes back to a numpy int16 array
                    audio_array = np.frombuffer(data, dtype=np.int16)
                    
                    # Set speaking flag before writing to stream (blocks until played)
                    is_playing = True
                    stream.write(audio_array)
                    is_playing = False
                    
                    playback_queue.task_done()
                except queue.Empty:
                    is_playing = False
                    continue
                except Exception as e:
                    print(f"\n[Realtime Player Error] Playback stream error: {e}")
    except Exception as e:
        print(f"\n[Realtime Player Error] Failed to open output stream: {e}")
    finally:
        print("[Realtime Player] Playback worker thread stopped.")

def clear_playback_queue():
    """
    Clears all queued audio chunks. Used on barge-in / interruption
    to stop Jarvis speaking immediately.
    """
    while not playback_queue.empty():
        try:
            playback_queue.get_nowait()
            playback_queue.task_done()
        except queue.Empty:
            break
        except ValueError:
            # task_done called too many times
            break

async def start_realtime_session():
    """
    Starts a real-time, low-latency, bidirectional voice session with Gemini.
    Captures mic input, streams it to the Gemini Live endpoint, receives audio
    and search grounding response, and plays it back.
    """
    if not config.GEMINI_API_KEY:
        print("[Realtime Error] GEMINI_API_KEY is not configured in .env file.")
        return
        
    loop = asyncio.get_running_loop()
    
    # Reset thread events and clear queues
    stop_playback_event.clear()
    clear_playback_queue()
    while not input_queue.empty():
        input_queue.get_nowait()
        
    # Start playback worker thread
    play_thread = threading.Thread(target=playback_worker, daemon=True)
    play_thread.start()
    
    # Define audio input callback for sounddevice RawInputStream
    def mic_callback(indata, frames, time_info, status):
        if status:
            print(f"[Realtime Mic Warning] {status}", file=sys.stderr)
        # Put raw bytes into the asyncio queue thread-safely
        loop.call_soon_threadsafe(input_queue.put_nowait, bytes(indata))
        
    # Initialize the Gemini GenAI Client
    client = genai.Client(api_key=config.GEMINI_API_KEY)
    
    # Configure session: spoken audio response & web search grounding
    # We choose "Puck" as the prebuilt voice config
    session_config = types.LiveConnectConfig(
        response_modalities=[types.Modality.AUDIO],
        speech_config=types.SpeechConfig(
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck")
            )
        ),
        tools=[{"google_search": {}}],  # Enables web search grounding
        system_instruction=(
            "You are Jarvis, a personal voice assistant. "
            "You must ALWAYS address the user as 'Kajal maam'. "
            "Be brief, witty, friendly, and natural. Respond in a mix of Hindi, English, "
            "or Hinglish based on how Kajal maam speaks to you. "
            "Your default location is Prayagraj. If Kajal maam asks about weather or news, use real data via the search tool. "
            "Do NOT explain that you are running a search, fetching data, or using tools (e.g. do NOT say 'Fetching weather data' or 'Let me query the weather'). "
            "Simply run the search and output only the direct, clean final answer to Kajal maam."
        ),
        generation_config=types.GenerationConfig(
            temperature=0.7,
        )
    )
    
    # Mic settings: 16-bit PCM, 16kHz, mono (required format for Gemini Live)
    mic_samplerate = 16000
    mic_channels = 1
    mic_chunk_size = 1024
    
    print("\n" + "=" * 50)
    print("      STARTING JARVIS REALTIME LIVE VOICE SESSION")
    print("      Speak naturally. Jarvis will listen and reply.")
    print("      Say 'exit live mode' or press Ctrl+C to stop.")
    print("=" * 50 + "\n")
    
    try:
        # Connect asynchronously to Gemini Live Endpoint
        async with client.aio.live.connect(model=config.GEMINI_LIVE_MODEL, config=session_config) as session:
            
            # Start the mic input stream
            mic_stream = sd.RawInputStream(
                samplerate=mic_samplerate,
                channels=mic_channels,
                dtype='int16',
                blocksize=mic_chunk_size,
                callback=mic_callback
            )
            
            async def send_loop():
                """Reads mic chunks from input_queue and streams to Gemini Live API."""
                # Clear any audio captured by the callback thread while the WebSocket was connecting
                while not input_queue.empty():
                    try:
                        input_queue.get_nowait()
                        input_queue.task_done()
                    except (asyncio.QueueEmpty, ValueError):
                        break
                        
                with mic_stream:
                    print("[Realtime] Microphone stream activated. Listening...")
                    while True:
                        audio_data = await input_queue.get()
                        # If Jarvis is currently speaking (playing output speaker audio),
                        # skip sending mic input to prevent acoustic echo feedback loop.
                        if not is_playing:
                            await session.send_realtime_input(
                                audio=types.Blob(data=audio_data, mime_type="audio/pcm;rate=16000")
                            )
                        input_queue.task_done()
                        
            async def receive_loop():
                """Receives streaming audio and grounding text from Gemini Live API."""
                print("[Realtime] Ready to receive responses...")
                first_chunk = True
                
                async for message in session.receive():
                    # Handle server content (text / audio chunks)
                    if message.server_content is not None:
                        # 1. Check for barge-in interruption (user started speaking over model)
                        if message.server_content.interrupted:
                            print("\n[Realtime] Jarvis interrupted. Stopping speech.")
                            clear_playback_queue()
                            first_chunk = True
                            continue
                            
                        # 2. Check for model turn
                        model_turn = message.server_content.model_turn
                        if model_turn is not None:
                            for part in model_turn.parts:
                                # Print generated text transcript in console if available
                                if part.text:
                                    if first_chunk:
                                        print("\nJarvis: ", end="", flush=True)
                                        first_chunk = False
                                    print(part.text, end="", flush=True)
                                    
                                # Queue audio chunks to playback thread
                                if part.inline_data:
                                    playback_queue.put(part.inline_data.data)
                                    
                    # Print grounding details (like search query)
                    if message.tool_call is not None:
                        # If model is calling a tool like search
                        for call in message.tool_call.function_calls:
                            if call.name == "google_search":
                                print(f"\n[Grounding Search] Running query: {call.args}")
                                
            # Run send and receive loops concurrently
            await asyncio.gather(send_loop(), receive_loop())
            
    except asyncio.CancelledError:
        print("\n[Realtime] Session task cancelled.")
    except Exception as e:
        print(f"\n[Realtime Error] Session exception: {e}")
    finally:
        # Signal playback thread to exit
        stop_playback_event.set()
        playback_queue.put(None)
        play_thread.join(timeout=2.0)
        print("[Realtime] Session cleanup complete. Goodbye boss!")

if __name__ == "__main__":
    print("--- Jarvis Realtime Voice Session Standalone Test ---")
    print("Press Ctrl+C to terminate.")
    try:
        asyncio.run(start_realtime_session())
    except KeyboardInterrupt:
        print("\nRealtime session test ended by user.")
