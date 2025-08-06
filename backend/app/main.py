import os

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api.gh import router as gh_router
from app.api.chat import router as chat_router


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = '/home/kanak/.config/gcloud/application_default_credentials.json'

app = FastAPI(default_response_class=ORJSONResponse)

app.include_router(gh_router)
app.include_router(chat_router)

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
