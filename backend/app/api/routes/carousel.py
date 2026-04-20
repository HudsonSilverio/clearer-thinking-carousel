import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, HttpUrl

from app.services.scraper import scrape_post
from app.services.ai_generator import generate_content
from app.services.carousel_builder import build_slides
from app.services.image_renderer import render_slides

router = APIRouter(prefix="/carousel", tags=["carousel"])

# In-memory store: carousel_id -> metadata
_store: dict[str, dict] = {}


class GenerateRequest(BaseModel):
    url: HttpUrl


@router.post("/generate")
async def generate_carousel(body: GenerateRequest):
    url = str(body.url)
    if "clearerthinking.org/post/" not in url:
        raise HTTPException(
            status_code=400,
            detail="URL must be a Clearer Thinking blog post (clearerthinking.org/post/...)",
        )

    # 1 — Scrape
    try:
        scraped = await scrape_post(url)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Scraping failed: {e}")

    if not scraped["title"]:
        raise HTTPException(status_code=422, detail="Could not extract post content from that URL.")

    title = scraped["title"]
    takeaways = scraped["takeaways"]
    cover_image = scraped["cover_image"]

    # 2 — AI generation
    ai = await generate_content(title, takeaways)

    # 3 — Build HTML slides
    slides = build_slides(
        title=title,
        cover_image=cover_image,
        takeaways=takeaways,
        hook=ai["hook"],
        slide_headlines=ai["slide_headlines"],
    )

    # 4 — Render PNGs + PDF
    carousel_id = uuid.uuid4().hex
    rendered = await render_slides(slides, carousel_id)

    # 5 — Store metadata
    metadata = {
        "carousel_id": carousel_id,
        "url": url,
        "title": title,
        "slide_count": rendered["slide_count"],
        "caption": ai["caption"],
        "hashtags": ai["hashtags"],
        "slide_images": rendered["png_paths"],
        "pdf_path": rendered["pdf_path"],
    }
    _store[carousel_id] = metadata

    return metadata


@router.get("/{carousel_id}/slide/{slide_index}")
async def get_slide(carousel_id: str, slide_index: int):
    meta = _store.get(carousel_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Carousel not found.")

    images = meta["slide_images"]
    if slide_index < 0 or slide_index >= len(images):
        raise HTTPException(status_code=404, detail=f"Slide index {slide_index} out of range.")

    path = images[slide_index]
    return FileResponse(path, media_type="image/png")


@router.get("/{carousel_id}/pdf")
async def get_pdf(carousel_id: str):
    meta = _store.get(carousel_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Carousel not found.")

    return FileResponse(
        meta["pdf_path"],
        media_type="application/pdf",
        filename=f"carousel_{carousel_id}.pdf",
    )


@router.get("/{carousel_id}/info")
async def get_info(carousel_id: str):
    meta = _store.get(carousel_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Carousel not found.")

    return {
        "carousel_id": carousel_id,
        "title": meta["title"],
        "slide_count": meta["slide_count"],
        "caption": meta["caption"],
        "hashtags": meta["hashtags"],
    }
