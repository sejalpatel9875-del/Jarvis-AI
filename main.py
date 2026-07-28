"""
J.A.R.V.I.S. Desktop Voice Assistant Entry Point (PyQt6-based Orchestrator)

This script acts as the central orchestrator connecting the ui.py graphical
frontend to the underlying voice engines (stt.py/tts.py) and JarvisBrain (chatbot.py).
All blocking tasks (listening, thinking, speaking) are routed to background QThreads.
"""

import sys
import os
import time
from PyQt6.QtCore import QThread, pyqtSignal, QObject
from PyQt6.QtWidgets import QApplication

import config
import stt
import tts
import utils.helpers as helpers
import agents.memory as memory_agent
from agents.brain import JarvisBrain
from ui import JarvisUI

# Configure UTF-8 encoding for Windows command prompt
helpers.configure_encoding()

class CommandWorker(QThread):
    """
    QThread worker that processes text commands through JarvisBrain
    and synthesizes responses via TTS. Keeps the GUI thread responsive.
    """
    finished = pyqtSignal(str, str) # Emits (sender, response)
    status_changed = pyqtSignal(str) # Emits state ("thinking", "speaking", "idle")

    def __init__(self, brain, command_text):
        super().__init__()
        self.brain = brain
        self.command_text = command_text

    def run(self):
        # 1. Shift UI state to 'thinking'
        self.status_changed.emit("thinking")
        try:
            # Process prompt through JarvisBrain (Reasoner -> Executor -> Validator)
            reply, actions = self.brain.think(self.command_text)
        except Exception as e:
            reply = f"Error in brain execution: {str(e)}"
            actions = []
        
        # 2. Shift UI state to 'speaking' and run Text-to-Speech
        if reply:
            self.status_changed.emit("speaking")
            try:
                # speak() is blocking; offloading to thread keeps orb pulsing smoothly
                tts.speak(reply)
            except Exception as e:
                print(f"[Worker TTS Error] {e}")

        # 3. Restore UI state to 'idle'
        self.status_changed.emit("idle")
        self.finished.emit("Jarvis", reply)


class VoiceListenWorker(QThread):
    """
    QThread worker that triggers microphone capture and Speech-to-Text transcription.
    """
    command_detected = pyqtSignal(str)
    status_changed = pyqtSignal(str)

    def run(self):
        self.status_changed.emit("listening")
        try:
            # stt.listen() calibrates mic and captures audio.
            # timeout=8 blocks until speech starts.
            heard = stt.listen(timeout=8, phrase_time_limit=10)
        except Exception as e:
            print(f"[Worker STT Error] {e}")
            heard = ""
        
        self.command_detected.emit(heard)


class WakeWordWorker(QThread):
    """
    QThread worker that continuously listens in the background for the wake word ("Jarvis").
    """
    wake_word_detected = pyqtSignal(str) # Emits trailing command text if spoken

    def __init__(self, wake_word):
        super().__init__()
        self.wake_word = wake_word
        self.running = True
        self.wake_variants = [wake_word, "jarvas", "javas", "jervis", "gervis", "jarvice", "jarwis", "djarvis", "travis", "jarbus"]

    def run(self):
        while self.running:
            try:
                # Use a small listen window so the thread frequently checks the 'self.running' flag
                heard = stt.listen(timeout=4, phrase_time_limit=5)
                if not heard:
                    continue
                
                detected = False
                command = ""
                # Check for wake word or popular phonetical approximations
                for variant in self.wake_variants:
                    if variant in heard.lower():
                        detected = True
                        # Grab any command spoken after the wake word in the same breath
                        parts = heard.lower().split(variant, 1)
                        if len(parts) > 1:
                            command = parts[1].strip()
                        break
                
                if detected and self.running:
                    self.wake_word_detected.emit(command)
            except Exception as e:
                print(f"[WakeWordWorker Error] {e}")
                time.sleep(1) # Prevent CPU spinning on audio driver dropouts

    def stop(self):
        self.running = False


class JarvisCore(QObject):
    """
    Central Controller linking PyQt6 GUI signals to Jarvis background threads.
    Decoupled design: UI emits commands/mic clicks -> JarvisCore processes in threads -> UI updates.
    """
    def __init__(self, ui):
        super().__init__()
        self.ui = ui
        self.brain = JarvisBrain()
        self.wake_word = getattr(config, "WAKE_WORD", "jarvis")
        
        # Connect UI custom events to controllers
        self.ui.command_submitted.connect(self.handle_command)
        self.ui.mic_clicked.connect(self.trigger_mic_listening)
        
        # Thread handles
        self.command_thread = None
        self.listen_thread = None
        self.wake_thread = None
        
        # Play startup greeting and begin background wake word loop
        self.startup_greeting()

    def startup_greeting(self):
        user_title = memory_agent.get_user_title()
        greeting = f"System initialized, {user_title}. I am online and ready."
        
        # Run startup TTS in a background command thread
        self.handle_command(f"Say greeting: {greeting}", is_silent_prompt=True)

    def start_wake_word_loop(self):
        """Starts background thread watching for the wake word."""
        self.stop_all_active_workers(stop_wake=False) # Keep wake thread running if already active
        
        if not self.wake_thread or not self.wake_thread.isRunning():
            self.ui.update_status("idle")
            self.wake_thread = WakeWordWorker(self.wake_word)
            self.wake_thread.wake_word_detected.connect(self.handle_wake_word)
            self.wake_thread.start()
            self.ui.append_chat("System", "Wake word detection active. Speak 'Jarvis' to prompt.")

    def handle_wake_word(self, command):
        """Callback when background thread detects the wake word."""
        print(f"[Core] Wake word triggered! Spoken trail: '{command}'")
        
        # Stop background listening immediately to free the audio input device and prevent self-activation
        self.stop_all_active_workers(stop_wake=True)
        
        # Run wake acknowledgment in a separate worker QThread so it doesn't freeze the GUI
        class AcknowledgeWorker(QThread):
            finished = pyqtSignal()
            def run(self):
                try:
                    tts.speak("Yes Boss?")
                except Exception as e:
                    print(f"[Wake Acknowledge Error] {e}")
                self.finished.emit()
                
        self.ack_worker = AcknowledgeWorker()
        
        def on_ack_finished():
            if command:
                self.ui.append_chat("Boss", command)
                self.handle_command(command)
            else:
                self.trigger_mic_listening()
                
        self.ack_worker.finished.connect(on_ack_finished)
        self.ack_worker.start()

    def trigger_mic_listening(self):
        """Triggered via Mic UI button or wake word. Stops wake word loop and listens for a command."""
        self.stop_all_active_workers(stop_wake=True)
        
        self.listen_thread = VoiceListenWorker()
        self.listen_thread.status_changed.connect(self.ui.update_status)
        self.listen_thread.command_detected.connect(self.handle_voice_command)
        self.listen_thread.start()

    def handle_voice_command(self, command):
        """Processes voice command if detected, else returns to background wake word watching."""
        if command:
            self.ui.append_chat("Boss", command)
            self.handle_command(command)
        else:
            self.ui.append_chat("System", "No speech detected. Returning to standby.")
            self.start_wake_word_loop()

    def handle_command(self, text, is_silent_prompt=False):
        """Routes a text prompt to the LLM JarvisBrain thread."""
        self.stop_all_active_workers(stop_wake=True)
        
        # If it's a silent prompt (e.g. initial boot greeting), handle it specially
        if is_silent_prompt:
            class GreetingWorker(QThread):
                status_changed = pyqtSignal(str)
                finished = pyqtSignal(str, str)
                def run(self):
                    self.status_changed.emit("speaking")
                    tts.speak(text.replace("Say greeting: ", ""))
                    self.status_changed.emit("idle")
                    self.finished.emit("Jarvis", text.replace("Say greeting: ", ""))
            
            self.command_thread = GreetingWorker()
        else:
            self.command_thread = CommandWorker(self.brain, text)
            
        self.command_thread.status_changed.connect(self.ui.update_status)
        self.command_thread.finished.connect(self.on_command_finished)
        self.command_thread.start()

    def on_command_finished(self, sender, response):
        """Appends output response to chat log and returns to standby mode."""
        self.ui.append_chat(sender, response)
        self.start_wake_word_loop()

    def stop_all_active_workers(self, stop_wake=True):
        """Terminates active worker threads safely to clean state before starting another action."""
        if self.command_thread and self.command_thread.isRunning():
            self.command_thread.terminate()
            self.command_thread.wait()
            
        if self.listen_thread and self.listen_thread.isRunning():
            self.listen_thread.terminate()
            self.listen_thread.wait()
            
        if stop_wake and self.wake_thread and self.wake_thread.isRunning():
            self.wake_thread.stop()
            self.wake_thread.terminate()
            self.wake_thread.wait()


def main():
    # Initialize Qt GUI Application
    app = QApplication(sys.argv)
    
    # Initialize the UI window
    ui = JarvisUI()
    
    # Initialize the Orchestrator tying backend features to the UI
    core = JarvisCore(ui)
    
    # Display the modern window
    ui.show()
    
    # Execute loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
