from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.gh import router as gh_router
from app.api.chat import router as chat_router


app = FastAPI()

app.add_router(gh_router)
app.add_router(chat_router)

ORIGINS = ['*']
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,  
    allow_methods=["*"],
    allow_headers=["*"], 
)


@app.get("/")
async def read_root():
    return {"message": "Health check successful!"}
