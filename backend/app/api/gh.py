
import asyncio
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from app.schemas.gh import GithubRepository, GithubIngestRequest, GithubIngestResponse

from database import mongo_db
from utils.weaviate_manager import WeaviateManager
from utils.embedder import embedder
from utils.github_manager import GithubManager

router = APIRouter(prefix="/gh", tags=["GitHub"])



@router.get("/", response_model=list[GithubRepository])
async def get_all_repos(
    db = Depends(mongo_db)
) -> list[GithubRepository]:
    repos = list(db['repos'].find({}, {"_id": 0}))
    return repos


@router.post("/", response_model=GithubIngestResponse)
async def create_repo(
    payload: GithubIngestRequest,
    background_tasks: BackgroundTasks,
    db = Depends(mongo_db)
):
    try:
        repo_url = payload.repo_url
        repo_url = str(repo_url).lower().strip()
        repo_url = repo_url.rstrip('/')

        if db["repos"].find_one({"repo_url": repo_url}):
            raise HTTPException(status_code=409, detail="Repository already ingested")

        gh_manager = GithubManager(mongo_db=db)
        await gh_manager.ingest_repo(repo_url, embedder)

        return GithubIngestResponse(status="success", repo_url=repo_url)
    except RuntimeError as e:
        # All branches failed to process
        raise HTTPException(status_code=409, detail=str(e))