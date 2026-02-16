import numpy as np
import sounddevice as sd
import soundfile as sf
import tempfile
import os
from faster_whisper import WhisperModel

# Use large-v3-turbo for best speed/quality tradeoff.
# Runs fully local on CPU with int8 quantization — no cloud, no limits.
MODEL_SIZE = "large-v3-turbo"


class TranscriptionManager:
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        self.recording = False
        self.audio_data = []
        self.stream = None
        self.volume_level = 0.0
        self.model = None
        self._model_loaded = False

    def _ensure_model_loaded(self):
        if not self._model_loaded:
            print(f"Loading Whisper model ({MODEL_SIZE})...")
            self.model = WhisperModel(
                MODEL_SIZE, device="cpu", compute_type="int8"
            )
            self._model_loaded = True
            print("Model loaded.")

    def start_recording(self):
        self.recording = True
        self.audio_data = []

        def callback(indata, frames, time_info, status):
            if status:
                print(status)
            if self.recording:
                self.audio_data.append(indata.copy())
                self.volume_level = float(np.sqrt(np.mean(indata**2)))

        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            callback=callback,
        )
        self.stream.start()

    def stop_recording(self):
        self.recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        self.volume_level = 0.0

    def get_volume(self):
        return self.volume_level

    def transcribe_buffer(self):
        """Transcribe the recorded audio buffer. No length limits."""
        if not self.audio_data:
            return "No audio recorded."

        audio = np.concatenate(self.audio_data, axis=0).flatten()
        duration = len(audio) / self.sample_rate
        print(f"Recorded {duration:.1f}s of audio")

        # Write to temp file for faster-whisper
        tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        try:
            sf.write(tmp.name, audio, self.sample_rate)
            return self._transcribe_file(tmp.name)
        finally:
            os.unlink(tmp.name)

    def transcribe_file(self, filepath):
        """Transcribe an uploaded audio file. No length limits."""
        if not filepath:
            return "No file provided."
        return self._transcribe_file(filepath)

    def _transcribe_file(self, filepath):
        self._ensure_model_loaded()
        print("Transcribing...")
        segments, info = self.model.transcribe(
            filepath,
            language="en",
            vad_filter=True,           # skip silence for speed
            vad_parameters=dict(
                min_silence_duration_ms=500,
            ),
        )
        text = " ".join(seg.text for seg in segments).strip()
        print(f"Done. ({info.duration:.1f}s audio → {len(text)} chars)")
        return text
