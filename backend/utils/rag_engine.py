import re

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.language_models import BaseLanguageModel
from langchain_core.documents import Document


class RAGQueryEngine:
    def __init__(self, llm: BaseLanguageModel):
        self.llm = llm
        self.prompt = PromptTemplate.from_template(
            """Use the following pieces of context belonging to a GitHub repo to answer the question at the end.
If you don't know the answer, just say that you don't know. Don't make things up.
Explain things clearly for a beginner.
Mention the source at the end of the answer.
Return the result in markdown.

{context}

Question: {question}

Helpful Answer:"""
        )

    def format_docs(self, docs: list[Document]) -> str:
        tmp_prefix_pattern = re.compile(r"^/tmp/tmp[^/]+/")
        for doc in docs:
            if "source" in doc.metadata:
                doc.metadata["source"] = tmp_prefix_pattern.sub("", doc.metadata["source"])
        return "\n\n\n".join(
            f"Source: {doc.metadata['source']}\n\n{doc.page_content}" for doc in docs
        )

    def run_query(self, question: str, docs: list[Document]):
        context = self.format_docs(docs)
        chain = self.prompt | self.llm | StrOutputParser()
        return chain.stream({"context": context, "question": question})

    async def stream_query(self, question: str, docs: list[Document]):
        context = self.format_docs(docs)
        chain = self.prompt | self.llm | StrOutputParser()
        # async for chunk in chain.astream({"context": context, "question": question}):
        #     yield chunk
        for chunk in chain.stream({'context': context, 'question': question}):
            yield chunk


    

    # async def stream_query(self, question: str, docs: list[Document]):
    #     context = self.format_docs(docs)
    #     chain = self.prompt | self.llm | StrOutputParser()

    #     buffer = ""
    #     async for chunk in chain.astream({"context": context, "question": question}):
    #         buffer += chunk
    #         if "\n" in chunk or any(p in buffer for p in [". ", "? ", "! "]):
    #             yield buffer
    #             buffer = ""
    #     if buffer:  # send any remaining text
    #         yield buffer