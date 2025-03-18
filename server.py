from fastapi import FastAPI
from ragbot.chatbot import building_graph
import re

app = FastAPI()

vector_store = None
graph = None

@app.on_event("startup")
def startup_event():
    global vector_store, graph
    graph, vector_store = building_graph()


@app.post("/ask")
def ask(question: str):
    response = graph.invoke({"question": question})

    cleaned_text = re.sub(r'<think>.*?</think>\s*', '', response["answer"], flags=re.DOTALL)
    
    return cleaned_text
