from pydantic import BaseModel

class GithubRepository(BaseModel):
    id: str
    name: str
    full_name: str
    html_url: str
    description: str | None = None