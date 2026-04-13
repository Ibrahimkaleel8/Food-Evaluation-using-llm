import json
import os
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

CHROMA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "chroma_db"))
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "foundationDownload.json")

def load_usda_data():
    if not os.path.exists(DATA_PATH):
        print(f"Error: {DATA_PATH} not found.")
        print("Please download the USDA FoodData Central Foundation Foods dataset and place it there.")
        return []

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("FoundationFoods", [])

def main():
    print("Loading USDA Foundation Foods dataset...")
    foods = load_usda_data()
    
    if not foods:
        return

    documents = []
    for food in foods:
        description = food.get("description", "Unknown Food")
        fdc_id = food.get("fdcId", "Unknown ID")
        
        nutrients = food.get("foodNutrients", [])
        nutrient_strings = []
        for n in nutrients:
            details = n.get("nutrient", {})
            name = details.get("name", "Unknown Nutrient")
            amount = n.get("amount", 0.0)
            unit = details.get("unitName", "")
            nutrient_strings.append(f"- {name}: {amount} {unit}")
            
        content = f"Food: {description}\n\nNutrients:\n" + "\n".join(nutrient_strings)
        
        doc = Document(
            page_content=content,
            metadata={
                "food_name": description,
                "fdc_id": fdc_id,
                "source": "USDA FoodData Central"
            }
        )
        documents.append(doc)

    print(f"Parsed {len(documents)} food items. Generating embeddings...")
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    
    # Store in ChromaDB
    vectorstore = Chroma.from_documents(
        documents,
        embeddings,
        persist_directory=CHROMA_PATH,
        collection_name="usda_foods"
    )
    
    print(f"Successfully embedded and stored {len(documents)} documents in ChromaDB at {CHROMA_PATH}.")

if __name__ == "__main__":
    main()
