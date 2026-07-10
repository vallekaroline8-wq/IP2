from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(_file_).parent / ".env")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.auth import router as auth_router

app = FastAPI(
    title="SIGIP API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.get("/")
def inicio():
    return {
        "mensaje": "SIGIP Backend MySQL funcionando"
    }