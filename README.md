# 📄 Retrieval-Augmented Chatbot API

A **FastAPI-based RAG (Retrieval-Augmented Generation) chatbot** that answers user queries based on information extracted from a local `resume.json`.  
Supports rate-limiting, CORS for frontend integration, and retrieval with Hugging Face embeddings + Chroma vector store.

---

## 🚀 Features
✅ Retrieval-Augmented Generation using `langgraph`  
✅ OpenAI Sentiment embeddings
✅ Chroma vector database for document retrieval  
✅ FastAPI REST API ready for frontend integration  
✅ CORS configured for specific frontend URLs  
✅ Rate-limited endpoint to prevent abuse (10 requests per hour per IP)  
✅ Cleaned AI responses (removes `<think>` tags)

---

## 📂 Project Structure
```
.
├── main.py                 # FastAPI app and chatbot API
├── resume.json             # JSON knowledge base for retrieval
├── requirements.txt
└── README.md
```

---

## ⚙️ Technologies Used
- **FastAPI** - RESTful API framework
- **slowapi** - Rate limiting
- **langchain_huggingface / langchain_chroma** - Embeddings & Vector DB
- **Groq Deepseek model** - LLM backend
- **RecursiveCharacterTextSplitter** - Chunking JSON documents
- **LangChain Hub Prompt** - For RAG prompt template
- **CORS Middleware** - Frontend integration

---

## 🔑 API Endpoint

### `POST /ask`
- **Description**: Ask the chatbot a question and get a generated answer
- **Rate Limit**: 10 requests per hour per IP
- **Request JSON**:
```json
{
  "message": "Your question here"
}
```
- **Response JSON**:
```json
{
  "answer": "AI generated answer based on resume knowledge"
}
```

---

## 🌐 CORS Allowed Origins:
- `http://localhost:5173`
- `https://pandalow.github.io/`

---

## 📖 How It Works (RAG Pipeline)
1. Load and split `resume.json`
2. Store chunks in a Chroma vector database
3. Accept user question
4. Perform similarity search to retrieve relevant context
5. Format context and question into a RAG prompt
6. Generate response using the LLM (`deepseek-r1-distill-qwen-32b`)
7. Clean response (remove `<think>` tags)
8. Return the answer

---

## 🛠 Running the Project

### 1️⃣ Install Requirements
```bash
pip install -r requirements.txt
```

### 2️⃣ Start the API Server
```bash
uvicorn main:app --reload
```

---

## 📈 Example Usage (curl)
```bash
curl -X POST "http://localhost:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"message": "Tell me about your backend skills."}'
```

---

## ⚠️ Rate Limiting
- Limit: `10/hour` per IP
- Returns **429 Too Many Requests** if exceeded

---

## 📜 Notes
✅ LLM model used: `deepseek-r1-distill-qwen-32b` via Groq  
✅ Embedding model: `sentence-transformers/paraphrase-MiniLM-L6-v2`  
✅ Vector DB: `Chroma`  
✅ JSON schema customizable via JQ syntax

---

## 🤝 License
MIT License — Feel free to use and modify.
