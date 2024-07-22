from fastapi import FastAPI
from model import get_response

from datatypes import TextIn


app = FastAPI()


@app.get("/get")
async def home():
    return {"health_check": "OK"}


@app.post("/response")
async def response(request: TextIn):
    result = get_response(request.food_name)
    # response = json.loads(result)
    return result
