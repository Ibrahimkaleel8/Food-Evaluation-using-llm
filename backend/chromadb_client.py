import os
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings

CHROMA_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "chroma_db"))

_vectorstore = None

def get_vectorstore() -> Chroma:
    global _vectorstore
    if _vectorstore is None:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        _vectorstore = Chroma(
            persist_directory=CHROMA_PATH,
            embedding_function=embeddings,
            collection_name="usda_foods"
        )
    return _vectorstore


def retrieve_food_context(food_name: str, k: int = 3) -> str:
    try:
        if not os.path.exists(CHROMA_PATH):
            return "No USDA results found (Database missing)."
            
        vectorstore = get_vectorstore()
        docs = vectorstore.similarity_search(food_name, k=k)
        
        if not docs:
            return "No USDA results found."
            
        context = "\n\n".join([doc.page_content for doc in docs])
        return context
    except Exception as e:
        print(f"Retrieval error: {e}")
        return "No USDA results found."
