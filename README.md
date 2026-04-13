# FoodNutriWise

An AI-powered web application that predicts nutrients in foods and evaluates their health benefits using Google's Gemini LLM.

## Description

FoodNutriWise leverages the Gemini API to provide comprehensive nutritional analysis of various foods. Simply input a food name and receive:

- Detailed nutrient breakdown
- Health impact evaluation (beneficial/harmful)
- Recommended consumption frequency

## Tech Stack

- Backend: FastAPI
- Frontend: Streamlit
- LLM: Google Gemini API via LangChain
- Cache: ChromaDB (persistent caching for food queries)
- Python: 3.10+

## Project Structure

```
Food-Evaluation-using-llm/
├── backend/
│   ├── main.py          # FastAPI app & endpoints
│   ├── model.py         # LLM integration
│   ├── prompt.py        # Prompt templates
│   ├── config.py        # Configuration
│   ├── datatypes.py     # Data models
│   ├── chromadb_client.py # ChromaDB caching
│   └── .env.default     # Environment variables template
├── frontend/
│   └── streamlitapp.py  # Streamlit UI
├── docker-compose.yaml
├── run.py               # Python launcher
└── Makefile
```

## Installation

### Prerequisites

- Python 3.10+ or compatible
- Gemini API key from Google AI Studio

### Setup

1. Clone the repo
   ```bash
   git clone https://github.com/Ibrahimkaleel8/Food-Evaluation-using-llm.git
   cd Food-Evaluation-using-llm
   ```

2. Create and activate virtual environment
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/macOS
   source venv/bin/activate
   ```

3. Install dependencies
   ```bash
   pip install -r backend/requirements.txt
   pip install -r frontend/requirements.txt
   ```

4. Create `.env` file in `backend/` folder
   ```env
   GOOGLE_API_KEY=your_api_key_here
   ```

## Running the Application

### Option 1: Run API and Frontend separately (no Poetry)
Open two terminals and run:

- API (FastAPI):
  ```bash
  python -m uvicorn backend.main:app --host 0.0.0.0 --port 3000 --reload
  ```
- Frontend (Streamlit):
  ```bash
  python -m streamlit run frontend/streamlitapp.py
  ```

### Option 2: Docker
```bash
docker compose up
```

After starting, access the app at:
- Frontend: http://localhost:8501
- API: http://localhost:3000

## API Endpoints

| Method | Endpoint     | Description              |
|--------|--------------|--------------------------|
| GET    | `/get`       | Health check             |
| POST   | `/response`  | Get food nutrition info  |

### Example Request
```bash
curl -X POST "http://localhost:3000/response" \
  -H "Content-Type: application/json" \
  -d '{"food_name": "banana"}'
```

## Benchmark results

| Metric | Baseline LLM | RAG Pipeline |
|--------|-------------|--------------|
| Calorie MAE | ~45 kcal | ~12 kcal |
| Overall accuracy (±10%) | ~61% | ~87% |
| Avg latency | 1.8s | 2.4s |
| Cache hit latency | — | 0.3s |
