import subprocess
import sys

print("Starting FoodNutriWise API (FastAPI)...")
backend = subprocess.Popen(
    [
        sys.executable,
        "-m",
        "uvicorn",
        "backend.main:app",
        "--host",
        "0.0.0.0",
        "--port",
        "3000",
        "--reload",
    ],
    creationflags=subprocess.CREATE_NEW_CONSOLE,
)

print("Starting FoodNutriWise Frontend (Streamlit)...")
frontend = subprocess.Popen(
    [sys.executable, "-m", "streamlit", "run", "frontend/streamlitapp.py"],
    creationflags=subprocess.CREATE_NEW_CONSOLE,
)

print("\nApplication started!")
print("Frontend: http://localhost:8501")
print("API: http://localhost:3000")
print("\nPress Ctrl+C to stop...")

try:
    backend.wait()
    frontend.wait()
except KeyboardInterrupt:
    backend.terminate()
    frontend.terminate()
    print("\nApplication stopped.")
