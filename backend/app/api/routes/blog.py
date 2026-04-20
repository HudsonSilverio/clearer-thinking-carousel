from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from app.services.scraper import scrape_post

router = APIRouter(prefix="/blog", tags=["blog"])


class ScrapeRequest(BaseModel):
    url: HttpUrl


class ScrapeResponse(BaseModel):
    url: str
    title: str
    cover_image: str | None
    takeaways: list[str]


@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_blog_post(body: ScrapeRequest):
    try:
        result = await scrape_post(str(body.url))
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to scrape URL: {e}")

    if not result["title"]:
        raise HTTPException(status_code=422, detail="Could not extract post content — is this a valid Clearer Thinking post URL?")

    return result
