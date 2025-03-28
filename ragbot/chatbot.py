from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from langchain_community.document_loaders import JSONLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain import hub
from typing_extensions import TypedDict, List
from langchain.schema import Document
from langgraph.graph import START, StateGraph
from langchain.chat_models import init_chat_model



def building_graph():
    
    llm = init_chat_model("deepseek-r1-distill-qwen-32b", model_provider="groq")

    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-MiniLM-L6-v2")
    vector_store = Chroma(embedding_function=embeddings)


    loader = JSONLoader(file_path="resume.json", jq_schema='.', text_content=False)
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    all_splits = text_splitter.split_documents(docs)

    # Index chunks
    _ = vector_store.add_documents(documents=all_splits)

    # Define prompt for question-answering
    prompt = hub.pull("rlm/rag-prompt")


    # Define state for application
    class State(TypedDict):
        question: str
        context: List[Document]
        answer: str


    # Define application steps
    def retrieve(state: State):
        retrieved_docs = vector_store.similarity_search(state["question"])
        return {"context": retrieved_docs}


    def generate(state: State):
        docs_content = "\n\n".join(doc.page_content for doc in state["context"])
        messages = prompt.invoke({"question": state["question"], "context": docs_content})
        response = llm.invoke(messages)
        return {"answer": response.content}


    # Compile application and test
    graph_builder = StateGraph(State).add_sequence([retrieve, generate])
    graph_builder.add_edge(START, "retrieve")
    graph = graph_builder.compile()

    return graph, vector_store