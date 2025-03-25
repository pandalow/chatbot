from fastapi import FastAPI
from ragbot.chatbot import building_graph
from fastapi.middleware.cors import CORSMiddleware
import re
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

app = FastAPI()

limiter = Limiter(key_func=get_remote_address, default_limits=["10/hour"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)



vector_store = None
graph = None

# ✅ Configure CORS to allow requests from specific front-end domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://pandalow.github.io/"],  # Allowed front-end origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all request headers
)

# ✅ Define the request schema
class Question(BaseModel):
    message: str

# ✅ Define the response schema
class Answer(BaseModel):
    answer: str

# ✅ Initialize the graph and vector store on application startup
@app.on_event("startup")
def startup_event():
    global vector_store, graph
    graph, vector_store = building_graph()

# ✅ Define the API endpoint for receiving questions and generating answers
@app.post("/ask", response_model=Answer)
@limiter.limit("10/hour")
def ask(question: Question):
    # Run the retrieval-augmented generation (RAG) graph
    response = graph.invoke({"question": question.message})

    # Clean up the response by removing any <think> tags and their content
    cleaned_text = re.sub(r'<think>.*?</think>\s*', '', response["answer"], flags=re.DOTALL)
    
    # Return the final cleaned answer
    return Answer(answer=cleaned_text)

