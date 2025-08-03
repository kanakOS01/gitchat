from fastapi import APIRouter

from app.schemas.gh import GithubRepository


router = APIRouter(prefix="/gh")


@router.get("/")
async def get_all_repos() -> list[GithubRepository]:
    pass


@router.post("/")
async def create_repo():
    pass