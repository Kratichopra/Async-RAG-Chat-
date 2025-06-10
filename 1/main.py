# # main.py
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from fastapi.responses import FileResponse
# from fastapi import FastAPI
# from pydantic import BaseModel
# from agent import chat_with_agent  # You already have this from previous steps
# templates = Jinja2Templates(directory="templates")
# app = FastAPI()

# class Query(BaseModel):
#     question: str
    

# @app.post("/chat")
# async def chat(query: Query):
#     try:
#         # print(query.question)
#         result = await chat_with_agent(query.question)
#         # print(result)
#         return {"response": result}
    
#     except Exception as e:
#         return {"error": str(e)}

# @app.get("/", response_class=HTMLResponse)
# async def get_form(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import asyncio
from agent import chat_with_agent  # make sure your function is imported

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_chat(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

class Query(BaseModel):
    question: str

@app.post("/ask")
async def ask_agent_json(data: Query):
    answer = await chat_with_agent(data.question)
    return {"response": answer}
