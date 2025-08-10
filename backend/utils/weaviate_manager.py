import asyncio
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

import weaviate
from langchain_weaviate.vectorstores import WeaviateVectorStore
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from config import settings


class WeaviateManager:
    def __init__(self):
        self.host = settings.WEAVIATE_HOST
        self.port = settings.WEAVIATE_PORT
        self.client = weaviate.connect_to_local(
            host=self.host,
            port=self.port,
        )

    @asynccontextmanager
    async def async_client(self) -> AsyncGenerator[weaviate.WeaviateClient, None]:
        client = weaviate.connect_to_local(
            host=self.host,
            port=self.port,
        )
        try:
            yield client
        finally:
            client.close()


    async def initialize_collection(self, collection_name: str) -> bool:
        async with self.async_client() as wc:
            if collection_name.lower() not in [c.lower() for c in wc.collections.list_all()]:
                wc.collections.create(name=collection_name)
            return True

    async def get_vector_store(self, collection_name: str, embeddings: Any) -> WeaviateVectorStore:
        if not self.client.is_connected():
            self.client.connect()
        return WeaviateVectorStore(
            client=self.client,
            text_key="files",
            index_name=collection_name,
            embedding=embeddings,
        )

    async def retrieve_context(self, question: str, collection: str, embeddings: Any, k: int = 5) -> str:
        vector_store = await self.get_vector_store(collection, embeddings)
        retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": k})
        docs = retriever.invoke(question)
        return docs
