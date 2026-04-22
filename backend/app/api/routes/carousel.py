import io
import uuid
import zipfile
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, HttpUrl

from app.services.scraper import scrape_post
from app.services.ai_generator import generate_content
from app.services.carousel_builder import build_slides
from app.services.image_renderer import render_slides

router = APIRouter(prefix="/carousel", tags=["carousel"])

_store: dict[str, dict] = {}


class GenerateRequest(BaseModel):
    url: HttpUrl


class TakeawayItem(BaseModel):
    headline: str
    body: str


class ColorsInput(BaseModel):
    slide_bg: str = "#E8EDF4"
    headline: str = "#555555"
    body: str = "#6B6B6B"
    progress_bar: str = "#E8A838"


class RenderCustomRequest(BaseModel):
    title: str
    cover_image: str | None = None
    takeaways: list[TakeawayItem]
    colors: ColorsInput = ColorsInput()


@router.post("/generate")
async def generate_carousel(body: GenerateRequest):
    url = str(body.url)
    if "clearerthinking.org/post/" not in url:
        raise HTTPException(
            status_code=400,
            detail="URL must be a Clearer Thinking blog post (clearerthinking.org/post/...)",
        )

    try:
        scraped = await scrape_post(url)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Scraping failed: {e}")

    if not scraped["title"]:
        raise HTTPException(status_code=422, detail="Could not extract post content from that URL.")

    title = scraped["title"]
    takeaways = scraped["takeaways"]
    cover_image = scraped["cover_image"]

    ai = await generate_content(title, takeaways)

    slides = build_slides(
        title=title,
        cover_image=cover_image,
        takeaways=takeaways,
    )

    carousel_id = uuid.uuid4().hex
    rendered = await render_slides(slides, carousel_id)

    metadata = {
        "carousel_id": carousel_id,
        "url": url,
        "title": title,
        "cover_image": cover_image,
        "slide_count": rendered["slide_count"],
        "takeaways": takeaways,
        "caption": ai["caption"],
        "hashtags": ai["hashtags"],
        "slide_images": rendered["png_paths"],
        "pdf_path": rendered["pdf_path"],
    }
    _store[carousel_id] = metadata

    return metadata


@router.post("/render-custom")
async def render_custom(body: RenderCustomRequest):
    """Re-render a carousel with edited content and custom colors."""
    takeaways = [{"headline": t.headline, "body": t.body} for t in body.takeaways]
    colors = {
        "slide_bg": body.colors.slide_bg,
        "headline": body.colors.headline,
        "body": body.colors.body,
        "progress_bar": body.colors.progress_bar,
    }

    slides = build_slides(
        title=body.title,
        cover_image=body.cover_image,
        takeaways=takeaways,
        colors=colors,
    )

    carousel_id = uuid.uuid4().hex
    rendered = await render_slides(slides, carousel_id)

    metadata = {
        "carousel_id": carousel_id,
        "slide_count": rendered["slide_count"],
        "slide_images": rendered["png_paths"],
        "pdf_path": rendered["pdf_path"],
    }
    _store[carousel_id] = {**metadata, "title": body.title, "cover_image": body.cover_image}

    return metadata


class RegenerateAIRequest(BaseModel):
    title: str
    takeaways: list[TakeawayItem]


@router.post("/regenerate-ai")
async def regenerate_ai(body: RegenerateAIRequest):
    """Re-run only the AI step (caption + hashtags) with current title/takeaways."""
    takeaways = [{"headline": t.headline, "body": t.body} for t in body.takeaways]
    ai = await generate_content(body.title, takeaways)
    return {"caption": ai["caption"], "hashtags": ai["hashtags"]}


@router.get("/{carousel_id}/zip")
async def get_zip(carousel_id: str):
    meta = _store.get(carousel_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Carousel not found.")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for i, path in enumerate(meta["slide_images"]):
            zf.write(path, f"slide_{i + 1:02d}.png")
    buf.seek(0)

    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=carousel_{carousel_id}.zip"},
    )


@router.get("/{carousel_id}/slide/{slide_index}")
async def get_slide(carousel_id: str, slide_index: int):
    meta = _store.get(carousel_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Carousel not found.")

    images = meta["slide_images"]
    if slide_index < 0 or slide_index >= len(images):
        raise HTTPException(status_code=404, detail=f"Slide index {slide_index} out of range.")

    return FileResponse(images[slide_index], media_type="image/png")


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
        "caption": meta.get("caption", ""),
        "hashtags": meta.get("hashtags", []),
        "takeaways": meta.get("takeaways", []),
    }
