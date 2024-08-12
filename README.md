# FoodNutriWise
A web application for predicting the nutrients in specific foods and evaluating their health benefits using a Large Language Model (LLM).

## Description
- FoodNutriWise is an AI-powered web application that leverages the Gemini API to provide comprehensive nutritional analysis of various foods.
- By simply inputting a food name, the application delivers detailed information about the nutrients present in the food.
- Additionally, it evaluates the health impact of the food—whether it is beneficial or harmful—and offers guidance on how frequently it can be consumed for optimal health.
- This tool aims to help users make informed dietary choices based on personalized nutritional insights.
- consists of two services frontend and backend.
- backend is exposed using fastapi.
- frontend is built using streamlit.

## Installation
### Prequisites
- python 3.9+
- virtualenv - `pip install virtualenv`
- Generate GeminiAPI key from here `https://aistudio.google.com/app/apikey`

### Setup
1. clone the repo ```
   git clone https://github.com/Ibrahimkaleel8/Food-Evaluation-using-llm.git```
2. Navigate to directory `cd Food-Evaluation-using-llm`
3. Create and activate a virtual environment
   1. In Linux and macos
   - `python3 -m venv venv`
   - `source venv/bin/activate`
   2. In windows
   - `python3 -m venv venv`
   -  `venv\Scripts\activate`

### Running the application
1. Using docker
    - ` docker compose up`
    - then navigate to browser and use this url :- `http://localhost:8501`
3. In local
   - ` make api`
   - then navigate to browser and use this url :- `http://localhost:8501`
  
