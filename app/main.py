from fastapi import FastAPI
from pydantic import BaseModel
from model import get_response
import gradio as gr
import uvicorn


class TextIn(BaseModel):
   food_name: str

app = FastAPI()

@app.get("/get")
def home():
    return {"health_check": "OK"}

@app.post('/response')
def response(request :TextIn):
    result = get_response(request.food_name)
    return result

demo = gr.Interface(
    fn=get_response,
    inputs=gr.Textbox(placeholder="Enter food name"),
       outputs="text",
       title="LLM App to Test Foods"
)

app = gr.mount_gradio_app(app, demo, path="/")

if __name__=='__main__':
    uvicorn.run(
        app="main:app",
        host = "0.0.0.0",  
        port=8000
    )