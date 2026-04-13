import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# LangSmith Tracing
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2", "true")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "nutriwise-pro")
langchain_api_key = os.getenv("LANGCHAIN_API_KEY")
if langchain_api_key:
    os.environ["LANGCHAIN_API_KEY"] = langchain_api_key

GOOGLE_API_KEY = "GOOGLE_API_KEY"
GEMINI_MODEL = "gemini-2.5-flash"
FORMAT_INSTRUCTIONS = "format_instructions"
FORMAT_INSTRUCTIONS2 = "format_instructions2"
FORMAT_INSTRUCTIONS3 = "format_instructions3"
FOOD_NAME = "food_name"
INGREDIENTS = "ingredients"
FOOD_TYPE = "food_type"
NUTRIENTS = "nutrients"
NOT_A_FOOD = "not a food"
NAME = "name"
PROTEIN = "protein"
FATS = "fats"
CARBOHYDRATES = "carbohydrates"
VITAMINS = "vitamins"
MINERALS = "minerals"
SUMMARY = "summary"
