import os
import tempfile
import webbrowser
import threading
from flask import Flask, request, jsonify, send_from_directory
from backend_logic import TranscriptionManager

app = Flask(__name__)
manager = TranscriptionManager()

UPLOAD_DIR = tempfile.mkdtemp()


@app.route("/")
def index():
    return send_from_directory(os.path.dirname(__file__), "index.html")


@app.route("/transcribe", methods=["POST"])
def transcribe():
    if "audio" not in request.files:
        return jsonify({"error": "No audio file"}), 400

    audio_file = request.files["audio"]
    tmp_path = os.path.join(UPLOAD_DIR, "upload.wav")
    audio_file.save(tmp_path)

    try:
        text = manager.transcribe_file(tmp_path)
        return jsonify({"text": text})
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


if __name__ == "__main__":
    port = 8976
    threading.Timer(1.0, lambda: webbrowser.open(f"http://localhost:{port}")).start()
    print(f"\n  Open Whisper running at http://localhost:{port}\n")
    app.run(host="127.0.0.1", port=port, debug=False)
