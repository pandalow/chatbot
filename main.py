from fastapi import FastAPI, Request, Response
from ragbot.chatbot import building_graph
from fastapi.middleware.cors import CORSMiddleware
import re
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

app = FastAPI()

# ✅ CORS Middleware，makes sure preflight OPTIONS is handled
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://pandalow.github.io"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Rate Limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["10/hour"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ✅ request and response data model
class Question(BaseModel):
    message: str

class Answer(BaseModel):
    answer: str

vector_store = None
graph = None

# ✅ startup load graph and vector store
@app.on_event("startup")
def startup_event():
    global vector_store, graph
    graph, vector_store = building_graph()

# ✅ handle OPTIONS request, prevent CORS 400 error
@app.options("/ask")
async def options_handler():
    return Response(status_code=200)

# ✅ slowapi security check - filter out OPTIONS request
def skip_options(**kwargs):
    request = kwargs.get("request")
    return request and request.method == "OPTIONS"

# ✅ main /ask interface, with rate limit and compatible OPTIONS
@app.post("/ask", response_model=Answer)
@limiter.limit("10/hour", exempt_when=skip_options)
async def ask(request: Request, question: Question):
    response = graph.invoke({"question": question.message})
    # clean <think> tag content
    cleaned_text = re.sub(r'<think>.*?</think>\s*', '', response["answer"], flags=re.DOTALL)
    return Answer(answer=cleaned_text)