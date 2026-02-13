from setuptools import setup

APP = ['main_ui.py']
DATA_FILES = [
    'config.json',
    'tekken.json',
    'model.safetensors'
]
OPTIONS = {
    'argv_emulation': True,
    'plist': {
        'CFBundleName': 'Open Whisper',
        'CFBundleDisplayName': 'Open Whisper',
        'CFBundleIdentifier': 'com.openwhisper.app',
        'CFBundleVersion': '0.2.0',
        'CFBundleShortVersionString': '0.2.0',
        'NSMicrophoneUsageDescription': 'Open Whisper needs microphone access to transcribe your speech.',
    },
    'packages': ['PySide6', 'mlx_audio', 'sounddevice', 'numpy', 'librosa', 'soundfile', 'pyperclip'],
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
