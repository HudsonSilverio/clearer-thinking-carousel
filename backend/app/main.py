from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.api.routes import blog

load_dotenv()

app = FastAPI(title="Clearer Thinking Carousel API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(blog.router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "ok"}
