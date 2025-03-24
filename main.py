from fastapi import FastAPI
from ragbot.chatbot import building_graph
from fastapi.middleware.cors import CORSMiddleware
import re
from pydantic import BaseModel


app = FastAPI()

vector_store = None
graph = None

# config CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://pandalow.github.io/"], 
    allow_credentials=True,
    allow_methods=["*"],  # allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # allow all headers
)

class Question(BaseModel):
    message: str

class Answer(BaseModel):
    answer: str

@app.on_event("startup")
def startup_event():
    global vector_store, graph
    graph, vector_store = building_graph()


@app.post("/ask")
def ask(question: Question):
    response = graph.invoke({"question": question.message})
    
    cleaned_text = re.sub(r'<think>.*?</think>\s*', '', response["answer"], flags=re.DOTALL)
    return Answer(answer=cleaned_text)
