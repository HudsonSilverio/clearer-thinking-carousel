import base64
import io
import uuid
import zipfile
from pathlib import Path

import httpx
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, HttpUrl

from app.services.scraper import scrape_post
from app.services.ai_generator import generate_content
from app.services.carousel_builder import build_slides, CTA_IMAGE_PATH
from app.services.image_renderer import render_slides, OUTPUT_DIR

router = APIRouter(prefix="/carousel", tags=["carousel"])

_store: dict[str, dict] = {}


# ─── Helper: fetch a remote image and return base64 data-URL ─────────────────

async def _to_data_url(url: str) -> str:
    """Convert a remote image URL to a base64 data-URL for reliable Playwright rendering."""
    if not url or not url.startswith("http"):
        return url
    try:
        async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
            r = await client.get(url)
            if r.status_code == 200:
                ct = r.headers.get("content-type", "image/jpeg").split(";")[0].strip()
                b64 = base64.b64encode(r.content).decode()
                return f"data:{ct};base64,{b64}"
    except Exception:
        pass
    return url


async def _fetch_bytes(url_or_path: str) -> bytes | None:
    """Fetch image bytes from a URL or local path (handles data: URLs too)."""
    if not url_or_path:
        return None
    if url_or_path.startswith("data:"):
        _, data = url_or_path.split(",", 1)
        try:
            return base64.b64decode(data)
        except Exception:
            return None
    if url_or_path.startswith("http"):
        try:
            async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
                r = await client.get(url_or_path)
                if r.status_code == 200:
                    return r.content
        except Exception:
            pass
        return None
    p = Path(url_or_path)
    return p.read_bytes() if p.exists() else None


# ─── Models ──────────────────────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    url: HttpUrl


class TakeawayItem(BaseModel):
    headline: str
    body: str
    slide_image: str | None = None


class ColorsInput(BaseModel):
    slide_bg: str = "#E8EDF4"
    headline: str = "#555555"
    body: str = "#6B6B6B"
    progress_bar: str = "#E8A838"


class TypographyInput(BaseModel):
    headline_font: str = "Source Serif 4"
    body_font: str = "Plus Jakarta Sans"
    headline_size: int = 42
    body_size: int = 28
    text_align: str = "left"


class RenderCustomRequest(BaseModel):
    title: str
    cover_image: str | None = None
    takeaways: list[TakeawayItem]
    colors: ColorsInput = ColorsInput()
    typography: TypographyInput = TypographyInput()


# ─── Endpoints ───────────────────────────────────────────────────────────────

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

    # Prefetch cover image as base64 so Playwright renders it reliably
    if cover_image:
        cover_image = await _to_data_url(cover_image)

    ai = await generate_content(title, takeaways)

    slides = build_slides(title=title, cover_image=cover_image, takeaways=takeaways)

    carousel_id = uuid.uuid4().hex
    rendered = await render_slides(slides, carousel_id)

    metadata = {
        "carousel_id": carousel_id,
        "url": url,
        "title": title,
        "cover_image": scraped["cover_image"],   # return original URL to frontend
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
    """Re-render a carousel with edited content, colors, and typography."""
    colors = {
        "slide_bg":     body.colors.slide_bg,
        "headline":     body.colors.headline,
        "body":         body.colors.body,
        "progress_bar": body.colors.progress_bar,
    }
    typography = {
        "headline_font": body.typography.headline_font,
        "body_font":     body.typography.body_font,
        "headline_size": body.typography.headline_size,
        "body_size":     body.typography.body_size,
        "text_align":    body.typography.text_align,
    }

    # Prefetch cover image for Playwright reliability
    cover_image = body.cover_image
    if cover_image and cover_image.startswith("http"):
        cover_image = await _to_data_url(cover_image)

    # Prefetch slide images
    takeaways = []
    for t in body.takeaways:
        slide_image = t.slide_image
        if slide_image and slide_image.startswith("http"):
            slide_image = await _to_data_url(slide_image)
        takeaways.append({"headline": t.headline, "body": t.body, "slide_image": slide_image})

    slides = build_slides(
        title=body.title,
        cover_image=cover_image,
        takeaways=takeaways,
        colors=colors,
        typography=typography,
    )

    carousel_id = uuid.uuid4().hex
    rendered = await render_slides(slides, carousel_id)

    metadata = {
        "carousel_id": carousel_id,
        "slide_count": rendered["slide_count"],
        "slide_images": rendered["png_paths"],
        "pdf_path": rendered["pdf_path"],
    }
    _store[carousel_id] = {
        **metadata,
        "title": body.title,
        "cover_image": body.cover_image,
        "takeaways": [{"headline": t.headline, "body": t.body} for t in body.takeaways],
        "colors": colors,
        "typography": typography,
    }

    return metadata


@router.post("/render-pptx")
async def render_pptx(body: RenderCustomRequest):
    """Generate an editable PPTX for Google Slides import."""
    from app.services.pptx_builder import build_pptx

    colors = {
        "slide_bg":     body.colors.slide_bg,
        "headline":     body.colors.headline,
        "body":         body.colors.body,
        "progress_bar": body.colors.progress_bar,
    }
    typography = {
        "headline_font": body.typography.headline_font,
        "body_font":     body.typography.body_font,
        "headline_size": body.typography.headline_size,
        "body_size":     body.typography.body_size,
        "text_align":    body.typography.text_align,
    }
    takeaways = [{"headline": t.headline, "body": t.body} for t in body.takeaways]

    cover_bytes = await _fetch_bytes(body.cover_image) if body.cover_image else None
    cta_bytes   = CTA_IMAGE_PATH.read_bytes() if CTA_IMAGE_PATH.exists() else None

    slide_img_list: list[bytes | None] = []
    for t in body.takeaways:
        slide_img_list.append(await _fetch_bytes(t.slide_image) if t.slide_image else None)

    carousel_id = uuid.uuid4().hex
    out_path = OUTPUT_DIR / carousel_id / f"{carousel_id}.pptx"

    build_pptx(
        title=body.title,
        takeaways=takeaways,
        colors=colors,
        typography=typography,
        out_path=out_path,
        cover_img_bytes=cover_bytes,
        cta_img_bytes=cta_bytes,
        slide_img_bytes_list=slide_img_list,
    )

    return FileResponse(
        str(out_path),
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=f"carousel_{carousel_id}.pptx",
        headers={"Content-Disposition": f"attachment; filename=carousel_{carousel_id}.pptx"},
    )


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
