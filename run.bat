@echo off
echo Starting FoodNutriWise API (FastAPI)...
start "FastAPI" cmd /k "uvicorn backend.main:app --host 0.0.0.0 --port 3000 --reload"

echo Starting FoodNutriWise Frontend (Streamlit)...
start "Streamlit" cmd /k "streamlit run frontend/streamlitapp.py"

echo Application started!
echo Frontend: http://localhost:8501
echo API: http://localhost:3000
pause
