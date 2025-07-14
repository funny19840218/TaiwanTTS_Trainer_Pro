import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog
from PyQt5.QtCore import Qt
import sounddevice as sd
from scipy.io.wavfile import write
import numpy as np
import os

class VoiceRecorder(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Voice Recorder")
        self.setGeometry(100, 100, 600, 400)

        self.script_path = None
        self.sentences = []
        self.current_sentence_index = 0
        self.is_recording = False
        self.recording = []

        self.init_ui()

    def init_ui(self):
        # Layouts
        main_layout = QVBoxLayout()
        top_layout = QHBoxLayout()
        sentence_layout = QHBoxLayout()
        controls_layout = QHBoxLayout()
        navigation_layout = QHBoxLayout()

        # Widgets
        self.load_button = QPushButton("Load Script")
        self.progress_label = QLabel("Progress: 0 / 0")
        self.sentence_label = QLabel("Please load a script.")
        self.sentence_label.setWordWrap(True)
        self.start_button = QPushButton("Start Recording")
        self.stop_button = QPushButton("Stop Recording")
        self.prev_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")

        # Add widgets to layouts
        top_layout.addWidget(self.load_button)
        top_layout.addWidget(self.progress_label)
        sentence_layout.addWidget(self.sentence_label)
        controls_layout.addWidget(self.start_button)
        controls_layout.addWidget(self.stop_button)
        navigation_layout.addWidget(self.prev_button)
        navigation_layout.addWidget(self.next_button)

        # Add layouts to main layout
        main_layout.addLayout(top_layout)
        main_layout.addLayout(sentence_layout)
        main_layout.addLayout(controls_layout)
        main_layout.addLayout(navigation_layout)

        self.setLayout(main_layout)

        # Connections
        self.load_button.clicked.connect(self.load_script)
        self.start_button.clicked.connect(self.start_recording)
        self.stop_button.clicked.connect(self.stop_recording)
        self.prev_button.clicked.connect(self.prev_sentence)
        self.next_button.clicked.connect(self.next_sentence)

        # Initial state
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.prev_button.setEnabled(False)
        self.next_button.setEnabled(False)

    def load_script(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Script File", "", "Text Files (*.txt)", options=options)
        if file_path:
            self.script_path = file_path
            with open(file_path, 'r', encoding='utf-8') as f:
                self.sentences = [line.strip() for line in f if line.strip()]
            self.current_sentence_index = 0
            self.update_sentence()
            self.update_progress()
            self.start_button.setEnabled(True)
            self.prev_button.setEnabled(True)
            self.next_button.setEnabled(True)

    def update_sentence(self):
        if self.sentences:
            self.sentence_label.setText(self.sentences[self.current_sentence_index])
        else:
            self.sentence_label.setText("Please load a script.")

    def update_progress(self):
        if self.sentences:
            self.progress_label.setText(f"Progress: {self.current_sentence_index + 1} / {len(self.sentences)}")
        else:
            self.progress_label.setText("Progress: 0 / 0")

    def start_recording(self):
        if self.sentences:
            self.is_recording = True
            self.recording = []
            self.start_button.setEnabled(False)
            self.stop_button.setEnabled(True)
            self.load_button.setEnabled(False)
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)

            # Start recording in a separate thread or use a callback
            self.stream = sd.InputStream(callback=self.audio_callback, samplerate=16000, channels=1, dtype='int16')
            self.stream.start()

    def audio_callback(self, indata, frames, time, status):
        """This is called (from a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        self.recording.append(indata.copy())

    def stop_recording(self):
        if self.is_recording:
            self.stream.stop()
            self.stream.close()
            self.is_recording = False
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.load_button.setEnabled(True)
            self.prev_button.setEnabled(True)
            self.next_button.setEnabled(True)

            # Save the recording
            self.save_recording()

    def save_recording(self):
        if self.recording:
            output_dir = "dataset/wavs"
            os.makedirs(output_dir, exist_ok=True)
            filename = f"{self.current_sentence_index + 1:04d}.wav"
            filepath = os.path.join(output_dir, filename)
            recording_data = np.concatenate(self.recording, axis=0)
            write(filepath, 16000, recording_data)
            print(f"Saved recording to {filepath}")

    def next_sentence(self):
        if self.current_sentence_index < len(self.sentences) - 1:
            self.current_sentence_index += 1
            self.update_sentence()
            self.update_progress()

    def prev_sentence(self):
        if self.current_sentence_index > 0:
            self.current_sentence_index -= 1
            self.update_sentence()
            self.update_progress()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    recorder = VoiceRecorder()
    recorder.show()
    sys.exit(app.exec_())
