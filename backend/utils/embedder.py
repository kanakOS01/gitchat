from langchain_google_genai import GoogleGenerativeAIEmbeddings

from config import settings


embedder = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    api_key=settings.GEMINI_API_KEY,
)