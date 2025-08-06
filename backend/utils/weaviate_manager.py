import asyncio
import os
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

import weaviate
from langchain_weaviate.vectorstores import WeaviateVectorStore
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate


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
            if collection_name not in [c.name for c in wc.collections.list_all(return_metadata=False)]:
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

    async def retrieve_context(self, question: str, vector_store: WeaviateVectorStore, k: int = 5) -> str:
        retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": k})
        docs = retriever.invoke(question)
        return self._format_docs(docs)

    async def query_with_rag(self, question: str, vector_store: WeaviateVectorStore, llm: Any, k: int = 5):
        context = await self.retrieve_context(question, vector_store, k=k)

        template = """Use the following pieces of context belonging to a GitHub repo to answer the question at the end.
If you don't know the answer, say so honestly. Don't make up information.
Explain as if the reader is a beginner. Always mention the source of the context.

{context}

Question: {question}

Helpful Answer:"""

        prompt = PromptTemplate.from_template(template)
        chain = prompt | llm | StrOutputParser()

        return chain.stream({"context": context, "question": question})

    def _format_docs(self, docs) -> str:
        for doc in docs:
            if "source" in doc.metadata:
                source = doc.metadata["source"]
                doc.metadata["source"] = source[5:] if source.startswith("repo/") else source

        return "\n\n\n".join(
            f"Source: {doc.metadata.get('source', 'unknown')}\n\n{doc.page_content}"
            for doc in docs
        )
