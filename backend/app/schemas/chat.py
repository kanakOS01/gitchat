from pydantic import BaseModel
from typing import Literal


class ChatRequest(BaseModel):
    question: str
    collection: str
    provider: Literal["openai"] = "openai"  # Future: "openai", "anthropic", etc.
