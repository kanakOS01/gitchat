from fastapi import APIRouter, HTTPException
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
async def chat(payload: ChatRequest):
    if payload.provider != "openai":
        raise HTTPException(status_code=400, detail="Only OpenAI provider is currently supported")
    
    # llm = ChatGoogleGenerativeAI(
    #     model="gemini-2.5-flash",
    #     temperature=0,
    #     google_api_key=settings.GOOGLE_API_KEY
    # )
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        api_key=settings.OPENAI_API_KEY
    )

    weaviate_manager = WeaviateManager()
    docs = await weaviate_manager.retrieve_context(
        question=payload.question,
        collection=payload.collection,
        embeddings=embedder
    )

    rag = RAGQueryEngine(llm=llm)

    async def generate():
        async for chunk in rag.stream_query(payload.question, docs):
            yield chunk

    return StreamingResponse(generate(), media_type="text/plain")
