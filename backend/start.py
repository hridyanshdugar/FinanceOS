"""Production start script. Installs dependencies and launches the server."""
import subprocess
import sys
import os

subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"])

volume_path = os.environ.get("RAILWAY_VOLUME_MOUNT_PATH", "/app/data")
os.environ.setdefault("DB_DIR", volume_path)

port = os.environ.get("PORT", "8000")
os.execvp(
    sys.executable,
    [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", port],
)
