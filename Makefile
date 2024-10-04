.PHONY: api
api:
		uvicorn backend.main:app --host 0.0.0.0 --port 3000 --reload & \
		streamlit run frontend/streamlitapp.py