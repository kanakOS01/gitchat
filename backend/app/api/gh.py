
from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.schemas.gh import GithubRepository, GithubIngestRequest, GithubIngestResponse

from database import GITCHAT_DB
from utils.weaviate_manager import WeaviateManager
from utils.embedder import embedder
from utils.github_manager import GithubManager

router = APIRouter(prefix="/gh", tags=["GitHub"])

weaviate_manager = WeaviateManager()
gh_manager = GithubManager(vector_store_manager=weaviate_manager)


@router.get("/", response_model=list[GithubRepository])
async def get_all_repos() -> list[GithubRepository]:
    repos = list(GITCHAT_DB["repos"].find({}, {"_id": 0}))
    return repos


@router.post("/", response_model=GithubIngestResponse)
async def create_repo(payload: GithubIngestRequest, background_tasks: BackgroundTasks):
    repo_url = payload.repo_url.lower().strip()

    if GITCHAT_DB["repos"].find_one({"repo_url": repo_url}):
        raise HTTPException(status_code=409, detail="Repository already ingested")

    def ingest():
        import asyncio
        asyncio.run(gh_manager.ingest_repo(repo_url, embedder))

    background_tasks.add_task(ingest)
    return GithubIngestResponse(status="processing", repo_url=repo_url)
