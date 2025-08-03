import asyncio
from contextlib import asynccontextmanager
import weaviate
from langchain_weaviate.vectorstores import WeaviateVectorStore
from typing import Any, AsyncGenerator


class WeaviateManager:
    def __init__(self, host: str = 'localhost', port: int = 8080):
        self.host = host
        self.port = port

    @asynccontextmanager
    async def client(self) -> AsyncGenerator[weaviate.WeaviateClient, None]:
        client = weaviate.connect_to_local(
            host=self.host,
            port=self.port,
        )
        try:
            yield client
        finally:
            client.close()

    async def initialize_collection(self, collection_name: str) -> bool:
        async with self.client() as wc:
            wc.collections.create(name=collection_name)
            return True

    async def get_vector_store(self, collection_name: str, embeddings: Any) -> WeaviateVectorStore:
        async with self.client() as wc:
            return WeaviateVectorStore(
                client=wc,
                text_key="files",
                index_name=collection_name,
                embedding=embeddings,
            )


async def main():
    wv = WeaviateManager()


if __name__ == "__main__":
    asyncio.run(main())
