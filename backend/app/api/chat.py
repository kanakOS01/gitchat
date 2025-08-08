from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import StreamingResponse
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

from app.schemas.chat import ChatRequest
from utils.weaviate_manager import WeaviateManager
from utils.rag_engine import RAGQueryEngine
from utils.embedder import embedder
from config import settings


router = APIRouter(prefix="/chat")


@router.post("/")
async def chat(
    payload: ChatRequest,
    authorization: str = Header(None)
):
    if payload.provider != "openai":
        raise HTTPException(status_code=400, detail="Only OpenAI provider is currently supported")
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    api_key = authorization.split(" ")[1]

    # llm = ChatGoogleGenerativeAI(
    #     model="gemini-2.5-flash",
    #     temperature=0,
    #     google_api_key=settings.GOOGLE_API_KEY
    # )
    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0,
        api_key=api_key,
        streaming=True
    )

    weaviate_manager = WeaviateManager()
    docs = await weaviate_manager.retrieve_context(
        question=payload.question,
        collection=payload.collection,
        embeddings=embedder
    )

    rag = RAGQueryEngine(llm=llm)

    return StreamingResponse(
        rag.stream_query(payload.question, docs),
        media_type="text/plain"
    )
