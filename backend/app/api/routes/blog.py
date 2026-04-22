from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from app.services.scraper import scrape_post

router = APIRouter(prefix="/blog", tags=["blog"])


class ScrapeRequest(BaseModel):
    url: HttpUrl


class TakeawayItem(BaseModel):
    headline: str
    body: str


class ScrapeResponse(BaseModel):
    url: str
    title: str
    cover_image: str | None
    takeaways: list[TakeawayItem]
    takeaway_count: int


@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_blog_post(body: ScrapeRequest):
    url = str(body.url)
    if "clearerthinking.org/post/" not in url:
        raise HTTPException(
            status_code=400,
            detail="URL must be a Clearer Thinking blog post (clearerthinking.org/post/...)",
        )

    try:
        result = await scrape_post(url)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to scrape URL: {e}")

    if not result["title"]:
        raise HTTPException(
            status_code=422,
            detail="Could not extract post content — is this a valid Clearer Thinking post URL?",
        )

    return result
