import sys
import pyperclip
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QTextEdit, QLabel, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QTimer, QSize, QThread, Signal, QRect
from PySide6.QtGui import QFont, QColor, QPainter, QPen, QBrush
from backend_logic import TranscriptionManager

class TranscriptionThread(QThread):
    finished = Signal(str)

    def __init__(self, manager):
        super().__init__()
        self.manager = manager

    def run(self):
        result = self.manager.transcribe()
        self.finished.emit(result)

class MicButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(300, 300)
        self.setCheckable(True)
        self.recording = False
        self.volume = 0.0
        self.bars = 32

    def set_volume(self, volume):
        self.volume = volume
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Center of the button
        center = self.rect().center()
        radius = 80

        # Draw the main button circle
        if self.isChecked():
            painter.setBrush(QBrush(QColor("#ff4444"))) # Red when recording
        else:
            painter.setBrush(QBrush(QColor("#646cff"))) # Blue/Purple when idle

        painter.setPen(Qt.NoPen)
        painter.drawEllipse(center, radius, radius)

        # Draw Mic Emoji
        painter.setPen(QPen(Qt.white))
        font = QFont("Arial", 60)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, "🎤")

        # Draw visualizer bars if recording
        if self.isChecked():
            painter.setPen(QPen(QColor("#44ff44"), 4))
            for i in range(self.bars):
                angle = float(i) / float(self.bars) * 360.0
                # Volume affects bar length
                # Added some randomness or scaling to make it look active
                bar_len = int(10 + float(self.volume) * 50)
                bar_len = max(0, min(bar_len, 40))

                painter.save()
                painter.translate(center)
                painter.rotate(angle)
                painter.drawLine(
                    int(radius + 10),
                    0,
                    int(radius + 10 + bar_len),
                    0
                )
                painter.restore()
            painter.end()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Open Whisper")
        self.setMinimumSize(900, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1a1a1a;
            }
            QTextEdit {
                background-color: #2a2a2a;
                color: #ffffff;
                border: 1px solid #444;
                border-radius: 8px;
                padding: 15px;
                font-size: 16px;
                line-height: 1.5;
            }
            QPushButton#copyButton {
                background-color: #444;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton#copyButton:hover {
                background-color: #555;
            }
            QLabel {
                color: #888;
                font-size: 14px;
            }
        """)

        self.manager = TranscriptionManager()
        self.setup_ui()

        # Timer for visualizer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_visualizer)
        self.timer.setInterval(50) # 20 fps

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(40)

        # Left Side: Microphone
        left_container = QVBoxLayout()
        left_container.setAlignment(Qt.AlignCenter)

        self.mic_button = MicButton()
        self.mic_button.clicked.connect(self.toggle_recording)
        left_container.addWidget(self.mic_button)

        self.status_label = QLabel("Click to start recording")
        self.status_label.setAlignment(Qt.AlignCenter)
        left_container.addWidget(self.status_label)

        main_layout.addLayout(left_container, 1)

        # Right Side: Transcription
        right_container = QVBoxLayout()

        top_bar = QHBoxLayout()
        top_bar.addStretch()
        self.copy_button = QPushButton("Copy All")
        self.copy_button.setObjectName("copyButton")
        self.copy_button.clicked.connect(self.copy_text)
        top_bar.addWidget(self.copy_button)
        right_container.addLayout(top_bar)

        self.text_area = QTextEdit()
        self.text_area.setPlaceholderText("Transcription will appear here...")
        self.text_area.setReadOnly(True)
        right_container.addWidget(self.text_area)

        main_layout.addLayout(right_container, 1)

    def toggle_recording(self):
        if self.mic_button.isChecked():
            # Start
            self.status_label.setText("Recording... Click again to stop")
            self.manager.start_recording()
            self.timer.start()
        else:
            # Stop
            self.status_label.setText("Processing transcription...")
            self.timer.stop()
            self.manager.stop_recording()
            self.mic_button.set_volume(0)
            self.start_transcription()

    def update_visualizer(self):
        volume = self.manager.get_volume()
        self.mic_button.set_volume(volume)

    def start_transcription(self):
        self.mic_button.setEnabled(False)
        self.thread = TranscriptionThread(self.manager)
        self.thread.finished.connect(self.on_transcription_finished)
        self.thread.start()

    def on_transcription_finished(self, text):
        self.text_area.setPlainText(text)
        self.status_label.setText("Transcription complete")
        self.mic_button.setEnabled(True)

    def copy_text(self):
        text = self.text_area.toPlainText()
        if text:
            pyperclip.copy(text)
            self.copy_button.setText("Copied!")
            QTimer.singleShot(2000, lambda: self.copy_button.setText("Copy All"))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
