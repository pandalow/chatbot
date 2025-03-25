from fastapi import FastAPI, Request, Response
from ragbot.chatbot import building_graph
from fastapi.middleware.cors import CORSMiddleware
import re
from pydantic import BaseModel
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

app = FastAPI()

# ✅ CORS Middleware，确保能处理 preflight OPTIONS
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

# ✅ 请求和响应数据模型
class Question(BaseModel):
    message: str

class Answer(BaseModel):
    answer: str

vector_store = None
graph = None

# ✅ 启动时加载 graph 和 vector store
@app.on_event("startup")
def startup_event():
    global vector_store, graph
    graph, vector_store = building_graph()

# ✅ 专门处理 OPTIONS，避免 CORS 400 报错
@app.options("/ask")
async def options_handler():
    return Response(status_code=200)

# ✅ slowapi 安全判断 - 过滤掉 OPTIONS 请求
def skip_options(**kwargs):
    request = kwargs.get("request")
    return request and request.method == "OPTIONS"

# ✅ 主 /ask 接口，带限流且兼容 OPTIONS
@app.post("/ask", response_model=Answer)
@limiter.limit("10/hour", exempt_when=skip_options)
async def ask(request: Request, question: Question):
    response = graph.invoke({"question": question.message})
    # 清除 <think> 标签内容
    cleaned_text = re.sub(r'<think>.*?</think>\s*', '', response["answer"], flags=re.DOTALL)
    return Answer(answer=cleaned_text)