# Jarvis: Personal AI Voice Assistant in Python

Jarvis is a modern, modular, and highly responsive personal voice assistant built in Python. It leverages Google's state-of-the-art **Gemini API** for advanced text chat and low-latency bidirectional voice sessions, edge-tts for high-quality natural-sounding speech generation, and local system/browser integration for desktop automation.

---

## Architecture Overview

```
jarvis/
├── main.py            # Entry point: Orchestrates wake-word listening, routes commands
├── stt.py             # Speech-to-Text: Dynamic noise calibration & Voice Activity Detection (VAD)
├── tts.py             # Text-to-Speech: Natural voice rendering using edge-tts
├── chatbot.py         # Standard Session: gemini-3.5-flash with history retention
├── realtime.py        # Realtime Voice: gemini-2.0-flash-exp for low-latency live voice & web search grounding
├── automation.py      # System Tasks: Web browser, YouTube playing, Google search, and desktop apps
├── config.py          # Configuration Loader: Loads environment settings from .env
└── requirements.txt   # Python Dependencies
```

---

## Key Features & Customizations

1. **Compilation-Free Audio Stack:**
   Standard python audio assistants require `pyaudio` and `pygame`, both of which require compiler setups (MSVC build tools/PortAudio development headers) which fail on modern Python runtimes (e.g. Python 3.14).
   * **Solution:** We transitioned to `sounddevice` and `soundfile` which ship with prebuilt DLLs for all major platforms (Windows, macOS, Linux). This makes the installation 100% compilation-free and out-of-the-box.
2. **Dynamic Noise-Aware VAD:**
   Avoids fixed-duration recordings. Jarvis listens, dynamically calculates the ambient noise ceiling, starts recording when you speak, and stops precisely 1.2 seconds after you finish speaking.
3. **Low-Latency Gemini Live Voice:**
   Uses WebSockets to open an async bidirectional live stream. You can speak and listen in real-time. Features automatic "barge-in" (speaking over Jarvis immediately aborts output audio playback).
4. **Google Search Grounding:**
   The realtime voice session includes Google Search tool execution to fetch up-to-date weather, news, and world facts.

---

## Setup & Installation

### 1. Prerequisites
Ensure you have Python 3.10+ installed. (Fully tested up to Python 3.14.6).

### 2. Clone and Install Dependencies
Navigate to the root directory and install dependencies:
```bash
# Install required libraries
py -m pip install -r requirements.txt
```

### 3. Obtain a Gemini API Key
1. Go to [Google AI Studio](https://aistudio.google.com/).
2. Create and copy an API Key.
3. Create a `.env` file in the project root:
   ```bash
   copy .env.example .env
   ```
4. Paste your key in `.env`:
   ```env
   GEMINI_API_KEY=AIzaSy...your_actual_key...
   ```

### 4. Customizing Settings
You can modify variables in your `.env` to configure your experience:
* `TTS_VOICE`: Configure your assistant's voice from Microsoft Edge Neural Voices.
  * English Male: `en-US-GuyNeural` (Default)
  * English Female: `en-US-AvaNeural`
  * Hindi Male: `hi-IN-MadhurNeural`
  * Hindi Female: `hi-IN-SwaraNeural`
* `WAKE_WORD`: Default is `jarvis`.
* `GEMINI_MODEL`: Default is `gemini-3.5-flash` (latest generation).
* `GEMINI_LIVE_MODEL`: Default is `gemini-2.0-flash-exp`.

---

## Running Jarvis

Start the voice assistant by running:
```bash
py main.py
```

### Voice Workflows:
1. **Wake Word Trigger:** Say **"Jarvis"**.
2. **Responses:**
   * Jarvis will speak *"Yes, boss?"* and wait. Speak your command.
   * Or speak the wake word and command in one breath: *"Jarvis, play Skyfall"*.
3. **Exit Assistant:** Say *"goodbye jarvis"* or press `Ctrl+C` in the console.

### Sample Command Formats:
* **Browser Automation:** *"open youtube"*, *"open browser"*, *"search google for best pizza recipes"*
* **App Automation:** *"open notepad"*, *"open calculator"*, *"open paint"*
* **Music Playback:** *"play despacito"* or *"play skyfall"* (launches auto-play YouTube stream)
* **Live Mode / Grounding Search:** *"go live"*, *"what is the weather today"* or *"who is the current prime minister of India"* (activates low-latency live search grounded session). Say *"exit live mode"* to return to standard listening.
* **General AI Queries:** *"tell me a joke"*, *"explain quantum computing in simple Hinglish"*
