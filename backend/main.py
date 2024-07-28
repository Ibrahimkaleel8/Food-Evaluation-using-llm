from fastapi import FastAPI
from model import get_extracted_details

from datatypes import TextIn


app = FastAPI()


@app.get("/get")
async def home():
    return {"health_check": "OK"}


@app.post("/response")
async def response(request: TextIn):
    result = get_extracted_details(request.food_name)
    return result
