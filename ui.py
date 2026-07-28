"""
J.A.R.V.I.S. Desktop Voice Assistant UI (PyQt6-based)

This module provides a modern, animated, glassmorphic desktop interface
for the Jarvis voice assistant.

Features:
- Frameless window with custom drag-and-drop window title bar.
- Iron Man Arc Reactor-style central glowing energy ring (QPainter arcs & gradients).
- Multiple visual states:
  * "idle": slow pulse, gentle rotation, cyan-blue glow.
  * "listening": fast pulse, wave ripples, bright neon green/cyan.
  * "thinking": fast continuous rotation, violet/purple color shifting.
  * "speaking": breathing rhythm synchronized with a simulated sine wave.
- Scrollable Conversation Log (Glassmorphic look).
- Minimalist command QLineEdit input box with a glow on focus.
- Asynchronous Thread-safe slots and signals to communicate with main.py logic.
"""

import sys
import math
from PyQt6.QtCore import Qt, QTimer, QPoint, pyqtSignal, pyqtSlot, QSize
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
    QPushButton, QLabel, QTextBrowser, QGraphicsDropShadowEffect, QFrame
)
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QLinearGradient, QRadialGradient

class GlowingOrbWidget(QWidget):
    """
    Custom widget that draws the animated glowing energy ring representing
    the J.A.R.V.I.S. core.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.state = "idle" # idle, listening, thinking, speaking
        self.angle = 0
        self.pulse = 1.0
        self.pulse_dir = 1
        self.sine_phase = 0.0
        
        # High refresh rate animation timer (60 FPS = ~16ms interval)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)
        self.timer.start(16)
        
        # Set minimum size for the orb
        self.setMinimumSize(220, 220)

    def set_state(self, state: str):
        """Sets the current state of the orb and changes animation characteristics."""
        if state in ["idle", "listening", "thinking", "speaking"]:
            self.state = state
            self.update()

    def update_animation(self):
        """Timer callback that increments animation attributes according to the current state."""
        # 1. Rotation Angle
        if self.state == "idle":
            self.angle = (self.angle + 1) % 360
        elif self.state == "listening":
            self.angle = (self.angle + 2) % 360
        elif self.state == "thinking":
            self.angle = (self.angle + 5) % 360
        elif self.state == "speaking":
            self.angle = (self.angle + 1) % 360

        # 2. Pulse Scaling
        pulse_speed = 0.015
        if self.state == "listening":
            pulse_speed = 0.04
        elif self.state == "speaking":
            pulse_speed = 0.025
        elif self.state == "thinking":
            pulse_speed = 0.005 # Slow breathing during thinking

        self.pulse += self.pulse_dir * pulse_speed
        if self.pulse >= 1.15:
            self.pulse = 1.15
            self.pulse_dir = -1
        elif self.pulse <= 0.88:
            self.pulse = 0.88
            self.pulse_dir = 1

        # 3. Sine Wave for Voice Speaking Simulation
        self.sine_phase += 0.15
        
        # Trigger redrawing of the widget
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        width = self.width()
        height = self.height()
        center_x = width // 2
        center_y = height // 2
        radius = min(width, height) // 4
        
        # Core Colors based on current state
        if self.state == "idle":
            core_color = QColor(0, 229, 255, 230)      # Cyan #00e5ff
            glow_color = QColor(0, 184, 212, 40)       # Muted Teal
            bg_glow = QColor(0, 229, 255, 10)
        elif self.state == "listening":
            core_color = QColor(0, 230, 118, 240)      # Neon Green/Cyan-green
            glow_color = QColor(0, 230, 118, 55)       # Stronger green glow
            bg_glow = QColor(0, 230, 118, 20)
        elif self.state == "thinking":
            # Color cycling between Cyan/Blue and Violet/Purple
            shift = int((math.sin(self.sine_phase * 0.2) + 1.0) * 60)
            core_color = QColor(100 + shift, 0, 255, 240) # Shifting violet
            glow_color = QColor(100 + shift, 0, 255, 45)
            bg_glow = QColor(100 + shift, 0, 255, 15)
        elif self.state == "speaking":
            # Sync pulse with mock speech levels
            amplitude_offset = abs(math.sin(self.sine_phase)) * 0.15
            self.pulse = 0.95 + amplitude_offset
            core_color = QColor(0, 145, 234, 230)      # Deep Electric Blue
            glow_color = QColor(0, 145, 234, 50)
            bg_glow = QColor(0, 145, 234, 15)

        # Draw outer background radial glow
        grad = QRadialGradient(center_x, center_y, radius * 2.5)
        grad.setColorAt(0.0, bg_glow)
        grad.setColorAt(0.7, glow_color)
        grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(grad))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(center_x - int(radius * 2.2), center_y - int(radius * 2.2), int(radius * 4.4), int(radius * 4.4))

        # Pulsed radius calculation
        r_pulsed = int(radius * self.pulse)

        # Draw outer rotating ring arcs (Arc Reactor Look)
        pen_outer = QPen(core_color, 2, Qt.PenStyle.SolidLine)
        painter.setPen(pen_outer)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # 3 Segments rotating
        painter.drawArc(center_x - r_pulsed, center_y - r_pulsed, r_pulsed * 2, r_pulsed * 2, (self.angle) * 16, 70 * 16)
        painter.drawArc(center_x - r_pulsed, center_y - r_pulsed, r_pulsed * 2, r_pulsed * 2, (self.angle + 120) * 16, 70 * 16)
        painter.drawArc(center_x - r_pulsed, center_y - r_pulsed, r_pulsed * 2, r_pulsed * 2, (self.angle + 240) * 16, 70 * 16)

        # Draw secondary inner ring rotating counter-clockwise
        pen_inner = QPen(core_color, 1, Qt.PenStyle.DashLine)
        painter.setPen(pen_inner)
        r_inner = int(r_pulsed * 0.75)
        painter.drawArc(center_x - r_inner, center_y - r_inner, r_inner * 2, r_inner * 2, (-self.angle * 1.5) * 16, 280 * 16)

        # Draw core solid glowing center node
        radial_core = QRadialGradient(center_x, center_y, r_pulsed * 0.4)
        radial_core.setColorAt(0.0, QColor(255, 255, 255, 255))
        radial_core.setColorAt(0.5, core_color)
        radial_core.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(radial_core))
        painter.setPen(Qt.PenStyle.NoPen)
        r_center = int(r_pulsed * 0.4)
        painter.drawEllipse(center_x - r_center, center_y - r_center, r_center * 2, r_center * 2)

        # Draw concentric target reticles (Tech HUD accents)
        pen_reticle = QPen(core_color, 1, Qt.PenStyle.SolidLine)
        painter.setPen(pen_reticle)
        r_reticle = int(r_pulsed * 1.15)
        # Small crosshairs on the edge of reticle
        painter.drawLine(center_x - r_reticle - 10, center_y, center_x - r_reticle + 2, center_y)
        painter.drawLine(center_x + r_reticle - 2, center_y, center_x + r_reticle + 10, center_y)
        painter.drawLine(center_x, center_y - r_reticle - 10, center_x, center_y - r_reticle + 2)
        painter.drawLine(center_x, center_y + r_reticle - 2, center_x, center_y + r_reticle + 10)


class CustomTitleBar(QWidget):
    """Custom titlebar for the frameless main window."""
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(36)
        
        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 10, 0)
        layout.setSpacing(10)
        
        # Title Label
        self.title_label = QLabel("J.A.R.V.I.S.  AI  OPERATING  SYSTEM", self)
        self.title_label.setStyleSheet("color: #7a889b; font-family: 'Inter'; font-size: 11px; font-weight: bold; letter-spacing: 2px;")
        
        # Window controls layout
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(8)
        
        # Minimize button
        self.min_btn = QPushButton(self)
        self.min_btn.setFixedSize(14, 14)
        self.min_btn.setStyleSheet("QPushButton { background-color: #ffd600; border-radius: 7px; border: none; } QPushButton:hover { background-color: #ffea00; }")
        self.min_btn.clicked.connect(self.parent.showMinimized)
        
        # Close button
        self.close_btn = QPushButton(self)
        self.close_btn.setFixedSize(14, 14)
        self.close_btn.setStyleSheet("QPushButton { background-color: #ff1744; border-radius: 7px; border: none; } QPushButton:hover { background-color: #ff5252; }")
        self.close_btn.clicked.connect(self.parent.close)
        
        layout.addWidget(self.title_label)
        layout.addStretch()
        layout.addWidget(self.min_btn)
        layout.addWidget(self.close_btn)
        
        # Mouse drag parameters
        self.drag_position = QPoint()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.parent.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.parent.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()


class JarvisUI(QMainWindow):
    """
    Main Desktop User Interface for J.A.R.V.I.S.
    """
    # Signal emitted when a text command is typed or STT processes a voice command
    command_submitted = pyqtSignal(str)
    
    # Signal emitted when the user presses the voice mic button
    mic_clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("J.A.R.V.I.S. AI OS")
        self.resize(520, 780)
        
        # Make the window frameless and transparent
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowSystemMenuHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        # Setup UI
        self.init_ui()
        
    def init_ui(self):
        # Base container widget (needed for custom rounded corners & styling)
        self.central_widget = QWidget(self)
        self.central_widget.setObjectName("CentralWidget")
        
        # Glassmorphic Dark UI Theme stylesheet
        self.central_widget.setStyleSheet("""
            QWidget#CentralWidget {
                background-color: qlineargradient(spread:pad, x1:0.5, y1:0, x2:0.5, y2:1, 
                    stop:0 rgba(10, 10, 16, 252), 
                    stop:1 rgba(5, 5, 8, 255));
                border: 1px solid rgba(0, 229, 255, 30);
                border-radius: 16px;
            }
        """)
        self.setCentralWidget(self.central_widget)
        
        # Window Shadow
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(25)
        shadow.setColor(QColor(0, 229, 255, 35))
        shadow.setOffset(0, 0)
        self.central_widget.setGraphicsEffect(shadow)
        
        # Main layout
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(5, 5, 5, 15)
        main_layout.setSpacing(10)
        
        # Title Bar
        self.title_bar = CustomTitleBar(self)
        main_layout.addWidget(self.title_bar)
        
        # Animated Orb Widget Container
        orb_container = QWidget(self)
        orb_layout = QVBoxLayout(orb_container)
        orb_layout.setContentsMargins(0, 10, 0, 10)
        
        self.orb = GlowingOrbWidget(self)
        orb_layout.addWidget(self.orb, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Status Text label
        self.status_label = QLabel("SYSTEM ONLINE", self)
        self.status_label.setFont(QFont("Inter", 10, QFont.Weight.Bold))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #00e5ff; letter-spacing: 3px; font-weight: bold; margin-top: 5px;")
        orb_layout.addWidget(self.status_label)
        
        main_layout.addWidget(orb_container)
        
        # Scrollable Chat Log Browser (Glassmorphic)
        self.chat_log = QTextBrowser(self)
        self.chat_log.setObjectName("ChatLog")
        self.chat_log.setStyleSheet("""
            QTextBrowser#ChatLog {
                background-color: rgba(15, 15, 25, 140);
                border: 1px solid rgba(255, 255, 255, 10);
                border-radius: 12px;
                color: #e0e6ed;
                font-family: 'Inter';
                font-size: 13px;
                padding: 15px;
                line-height: 1.6;
            }
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0, 229, 255, 50);
                min-height: 20px;
                border-radius: 3px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
        main_layout.addWidget(self.chat_log)
        
        # Console Log Header message
        self.append_chat("System", "J.A.R.V.I.S. Voice Engine & Autonomous OS core online.")
        
        # Bottom Command Input Layout
        input_container = QFrame(self)
        input_container.setStyleSheet("background-color: transparent;")
        
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(5, 5, 5, 5)
        input_layout.setSpacing(10)
        
        # command edit QLineEdit
        self.command_input = QLineEdit(self)
        self.command_input.setPlaceholderText("Type command or click Mic...")
        self.command_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(15, 15, 25, 180);
                border: 1px solid rgba(255, 255, 255, 12);
                border-radius: 20px;
                color: #ffffff;
                font-family: 'Inter';
                font-size: 13px;
                padding: 10px 15px;
            }
            QLineEdit:focus {
                border: 1px solid #00e5ff;
                background-color: rgba(15, 15, 25, 220);
            }
        """)
        self.command_input.returnPressed.connect(self.submit_typed_command)
        
        # Mic Trigger Button
        self.mic_btn = QPushButton(self)
        self.mic_btn.setFixedSize(40, 40)
        self.mic_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mic_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(0, 229, 255, 20);
                border: 1px solid rgba(0, 229, 255, 40);
                border-radius: 20px;
                color: #00e5ff;
                font-size: 16px;
                font-family: 'Segoe UI Symbol';
            }
            QPushButton:hover {
                background-color: rgba(0, 229, 255, 40);
                border: 1px solid #00e5ff;
            }
            QPushButton:pressed {
                background-color: rgba(0, 229, 255, 60);
            }
        """)
        self.mic_btn.setText("🎙️") # Unicode mic symbol
        self.mic_btn.clicked.connect(self.submit_mic_clicked)
        
        input_layout.addWidget(self.command_input)
        input_layout.addWidget(self.mic_btn)
        
        main_layout.addWidget(input_container)

    def submit_typed_command(self):
        """Processes and submits a typed user command."""
        text = self.command_input.text().strip()
        if text:
            self.command_input.clear()
            self.append_chat("Boss", text)
            self.command_submitted.emit(text)

    def submit_mic_clicked(self):
        """Propagates microphone action button click."""
        self.mic_clicked.emit()

    # --- Thread-Safe Slots Callable from Main Thread Orchestrator ---

    @pyqtSlot(str)
    def update_status(self, state: str):
        """
        Updates status label text and glowing orb animation.
        Available states: "idle", "listening", "thinking", "speaking"
        """
        # Formulate display string
        display_text = "READY"
        if state == "listening":
            display_text = "LISTENING..."
        elif state == "thinking":
            display_text = "THINKING..."
        elif state == "speaking":
            display_text = "SPEAKING..."
            
        self.status_label.setText(display_text)
        
        # Color shifting status labels based on current states
        if state == "listening":
            self.status_label.setStyleSheet("color: #00e676; letter-spacing: 3px; font-weight: bold; margin-top: 5px;")
        elif state == "thinking":
            self.status_label.setStyleSheet("color: #d500f9; letter-spacing: 3px; font-weight: bold; margin-top: 5px;")
        elif state == "speaking":
            self.status_label.setStyleSheet("color: #2979ff; letter-spacing: 3px; font-weight: bold; margin-top: 5px;")
        else:
            self.status_label.setStyleSheet("color: #00e5ff; letter-spacing: 3px; font-weight: bold; margin-top: 5px;")
            
        self.orb.set_state(state)

    @pyqtSlot(str, str)
    def append_chat(self, sender: str, message: str):
        """Appends formatted messages to scrollable conversation log view."""
        if sender == "System":
            formatted = f"<p style='margin: 3px 0; color: #7a889b;'><i>[System] {message}</i></p>"
        elif sender == "Boss":
            formatted = f"<p style='margin: 5px 0;'><span style='color: #00e5ff; font-weight: bold;'>You:</span> {message}</p>"
        else:
            # Format Jarvis assistant messages nicely (Hinglish/English mix)
            formatted = f"<p style='margin: 8px 0; padding: 6px; border-radius: 4px; background-color: rgba(0, 229, 255, 8);'><span style='color: #2979ff; font-weight: bold;'>Jarvis:</span> {message}</p>"
        
        self.chat_log.append(formatted)
        
        # Auto-scroll to the bottom
        scrollbar = self.chat_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    app = QApplication(sys.argv)
    ui = JarvisUI()
    ui.show()
    sys.exit(app.exec())
