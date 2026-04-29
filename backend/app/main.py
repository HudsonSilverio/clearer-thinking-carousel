import os
import sys
import asyncio

# Playwright requires ProactorEventLoop on Windows (SelectorEventLoop blocks subprocesses)
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from app.api.routes import blog, carousel, upload

load_dotenv()

_default_dir = Path(__file__).resolve().parent.parent / "generated_carousels"
GENERATED_DIR = Path(os.getenv("GENERATED_DIR", str(_default_dir)))
GENERATED_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Clearer Thinking Carousel API", version="2.0.0")

allowed_origins = [
    "http://localhost:3000",
    os.getenv("FRONTEND_URL", "http://localhost:3000"),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(blog.router, prefix="/api")
app.include_router(carousel.router, prefix="/api")
app.include_router(upload.router, prefix="/api")

app.mount(
    "/generated_carousels",
    StaticFiles(directory=str(GENERATED_DIR)),
    name="generated_carousels",
)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
