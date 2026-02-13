# Open Whisper

A native macOS application for long-form speech-to-text transcription using the **Voxtral-Mini-4B-Realtime-2602-fp16** model and **MLX**.

## Features

- **Native macOS Feel**: Built with PySide6 for a fast, responsive interface.
- **Privacy-First**: Runs entirely locally on your Mac (optimized for M-series chips).
- **High Accuracy**: Uses the latest Voxtral 4B model from Mistral AI.
- **Long-form Recording**: Record for extended periods with a large, easy-to-use microphone button.
- **Visual Feedback**: Live volume visualizer around the microphone button.
- **Copy to Clipboard**: One-click to copy your entire transcription.

## Requirements

- macOS (Apple Silicon M1/M2/M3/M4 recommended)
- Python 3.11+
- `uv` (for dependency management)

## Setup

1. **Install Dependencies**:
   ```bash
   uv sync
   ```

2. **Model Files**:
   The app expects `model.safetensors`, `config.json`, and `tekken.json` to be in the root directory.
   - You should already have `model.safetensors` (8GB+).
   - Metadata files (`config.json`, `tekken.json`) have been automatically downloaded.

## Usage

Run the app using the provided start script:
```bash
./start.sh
```

### Instructions:
1. Click the large **🎤** button to start recording.
2. Watch the green bars react to your voice volume.
3. Click the button again to stop recording.
4. Wait for the transcription to process (batch mode).
5. The full text will appear on the right side.
6. Click **Copy All** to copy the text to your clipboard.

## Packaging as a .app Bundle

To create a standalone macOS application:
```bash
uv pip install py2app
python setup.py py2app
```
The application will be located in the `dist/` folder.
