from .chatbot import building_graph

import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 获取 API Keys
groq_api_key = os.getenv("GROQ_API_KEY")
langsmith_api_key = os.getenv("LANGSMITH_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")


