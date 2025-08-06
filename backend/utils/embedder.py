from langchain_openai import OpenAIEmbeddings

from config import settings


embedder = OpenAIEmbeddings(
    model="text-embedding-3-large",
    dimensions=1024,
    api_key=settings.OPENAI_API_KEY,
)