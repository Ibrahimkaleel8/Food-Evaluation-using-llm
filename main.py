from fastapi import FastAPI
from pydantic import BaseModel
from model import get_response, Dietinfo

# import gradio as gr
import uvicorn
import json
from datatypes import TextIn


app = FastAPI()


@app.get("/get")
async def home():
    return {"health_check": "OK"}


@app.post("/response")
async def response(request: TextIn):
    result = get_response(request.food_name)
    response = json.loads(result)
    return response


# demo = gr.Interface(
#     fn=get_response,
#     inputs=gr.Textbox(placeholder="Enter food name"),
#        outputs="text",
#        title="LLM App to Test Foods"
# )

# app = gr.mount_gradio_app(app, demo, path="/")

# if __name__=='__main__':
#     uvicorn.run(
#         app="main:app",
#         host = "0.0.0.0",
#         port=3000,
#         reload=True
#     )
