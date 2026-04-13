from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import time
import json

from .model import get_extracted_details, get_rag_nutrition, llm
from .datatypes import TextIn, UserProfile
from .scoring import compute_health_score, score_label
from .analytics import log_query
from .prompt import RAG_NUTRITION_PROMPT
from langchain_core.prompts import PromptTemplate
from .chromadb_client import retrieve_food_context


app = FastAPI()

class QueryRequest(BaseModel):
    food_name: str
    profile: Optional[UserProfile] = None


@app.get("/get")
async def home():
    return {"health_check": "OK"}


@app.post("/response")
async def response(request: QueryRequest):
    start_time = time.time()
    result = get_rag_nutrition(request.food_name)
    latency_ms = (time.time() - start_time) * 1000.0

    out_dict = result.model_dump()
    
    # Calculate personalized score if profile is given
    if request.profile:
        p_score = compute_health_score(result, request.profile)
        out_dict["personalized_score"] = round(p_score, 2)
        out_dict["score_label"] = score_label(p_score)
    else:
        out_dict["personalized_score"] = out_dict["health_score"]
        out_dict["score_label"] = score_label(out_dict["health_score"])
        
    # Log the query
    log_data = out_dict.copy()
    log_data["latency_ms"] = latency_ms
    log_query(log_data)

    return out_dict


@app.post("/response/stream")
async def response_stream(request: QueryRequest):
    async def generate():
        start_time = time.time()
        
        usda_context = retrieve_food_context(request.food_name)
        prompt = PromptTemplate(
            template=RAG_NUTRITION_PROMPT,
            input_variables=["food_name", "usda_context"]
        )
        
        chain = prompt | llm
        
        full_text = ""
        try:
            async for chunk in chain.astream({"food_name": request.food_name, "usda_context": usda_context}):
                if chunk.content:
                    # Stream tokens
                    text_chunk = chunk.content.replace("\n", "\\n") # basic escaping for SSE
                    yield f"data: {json.dumps({'token': chunk.content})}\n\n"
                    full_text += chunk.content
                    
            yield "data: [DONE]\n\n"
            
            # Post-processing: log after stream completes
            # Parse full text to log it
            try:
                # remove backticks if present
                clean_json = full_text.strip("```json\n").strip("\n```").strip()
                res_dict = json.loads(clean_json)
                latency_ms = (time.time() - start_time) * 1000.0
                
                # Apply profiling logic
                if request.profile:
                    # Hack: recreate NutritionResponse to pass to scoring (ignoring validation for logging)
                    from .datatypes import NutritionResponse
                    n_res = NutritionResponse(**res_dict)
                    p_score = compute_health_score(n_res, request.profile)
                    res_dict["personalized_score"] = round(p_score, 2)
                else:
                    res_dict["personalized_score"] = res_dict.get("health_score", 0.0)
                    
                res_dict["latency_ms"] = latency_ms
                log_query(res_dict)
            except Exception as parse_e:
                print(f"Log error post-stream: {parse_e}")
                
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            yield "data: [DONE]\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")
