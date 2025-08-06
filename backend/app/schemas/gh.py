from pydantic import BaseModel, HttpUrl
from typing import List, Optional


class GithubIngestRequest(BaseModel):
    repo_url: HttpUrl


class GithubIngestResponse(BaseModel):
    status: str
    repo_url: HttpUrl


class GithubBranchMetadata(BaseModel):
    branch: str
    vs_collection: Optional[str]
    chunks: int
    error: Optional[str] = None


class GithubRepository(BaseModel):
    repo_url: HttpUrl
    repo_name: str
    owner: str
    created_at: str
    branches: List[GithubBranchMetadata]
