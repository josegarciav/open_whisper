import numpy as np
import sounddevice as sd
import threading
import queue
import time
import os
import soundfile as sf
from mlx_audio.stt.utils import load

class TranscriptionManager:
    def __init__(self, model_path=".", sample_rate=16000):
        self.model_path = model_path
        self.sample_rate = sample_rate
        self.recording = False
        self.audio_data = []
        self.stream = None
        self.model = None
        self.transcription_text = ""
        self.volume_level = 0.0
        self._stop_event = threading.Event()

        # Load model lazily
        self.model_loaded = False

    def load_model(self):
        if not self.model_loaded:
            print(f"Loading model from {self.model_path}...")
            # mlx-audio load can take a local path or repo id.
            # Since we have files in current dir, we pass current dir.
            self.model = load(self.model_path)
            self.model_loaded = True
            print("Model loaded successfully.")

    def start_recording(self):
        self.recording = True
        self.audio_data = []
        self.transcription_text = ""

        def callback(indata, frames, time, status):
            if status:
                print(status)
            if self.recording:
                self.audio_data.append(indata.copy())
                # Calculate volume level (RMS)
                self.volume_level = np.sqrt(np.mean(indata**2))

        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            callback=callback
        )
        self.stream.start()

    def stop_recording(self):
        self.recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        self.volume_level = 0.0

    def get_audio_buffer(self):
        if not self.audio_data:
            return None
        return np.concatenate(self.audio_data, axis=0)

    def transcribe(self, progress_callback=None):
        """Runs transcription on the recorded audio."""
        audio = self.get_audio_buffer()
        if audio is None or len(audio) == 0:
            return "No audio recorded."

        try:
            self.load_model()

            # Save to temporary wav file as mlx-audio's generate often expects a file path
            # or a numpy array depending on version. The usage said "audio.wav".
            temp_wav = "temp_recording.wav"
            sf.write(temp_wav, audio, self.sample_rate)

            print("Starting transcription...")
            # We use generate in batch mode as requested
            result = self.model.generate(temp_wav, transcription_delay_ms=480)

            if hasattr(result, 'text'):
                self.transcription_text = result.text
            else:
                self.transcription_text = str(result)

            # Cleanup
            if os.path.exists(temp_wav):
                os.remove(temp_wav)

            return self.transcription_text
        except Exception as e:
            print(f"Transcription error: {e}")
            return f"Error: {str(e)}"

    def get_volume(self):
        return self.volume_level
