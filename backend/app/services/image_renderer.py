import asyncio
import os
import uuid
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright
import PIL.JpegImagePlugin  # registers JPEG encoder required by Pillow's PDF plugin
from PIL import Image, ImageDraw
from app.utils.brand import SLIDE_WIDTH, SLIDE_HEIGHT

_default_dir = Path(__file__).resolve().parent.parent.parent / "generated_carousels"
OUTPUT_DIR = Path(os.getenv("GENERATED_DIR", str(_default_dir)))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _render_cta_image(slide: dict, out_path: Path) -> None:
    """Load cta-slide.png, scale to 1080×1080 (cover crop), add progress bar."""
    img = Image.open(slide["cta_image_path"]).convert("RGB")
    w, h = img.size
    scale = max(SLIDE_WIDTH / w, SLIDE_HEIGHT / h)
    nw = int(w * scale + 0.5)
    nh = int(h * scale + 0.5)
    img = img.resize((nw, nh), Image.LANCZOS)
    x = (nw - SLIDE_WIDTH) // 2
    y = (nh - SLIDE_HEIGHT) // 2
    img = img.crop((x, y, x + SLIDE_WIDTH, y + SLIDE_HEIGHT))

    draw = ImageDraw.Draw(img)
    bar_h = 8
    hex_col = slide["progress_bar_color"].lstrip("#")
    rgb = tuple(int(hex_col[i: i + 2], 16) for i in (0, 2, 4))
    draw.rectangle([0, SLIDE_HEIGHT - bar_h, SLIDE_WIDTH, SLIDE_HEIGHT], fill=rgb)

    img.save(str(out_path), "PNG")


def _render_slides_sync(slides: list[dict], carousel_id: str) -> dict:
    out_dir = OUTPUT_DIR / carousel_id
    out_dir.mkdir(parents=True, exist_ok=True)

    indexed_paths: list[tuple[int, str]] = []

    # ── HTML slides via Playwright ────────────────────────────────────────────
    html_slides = [s for s in slides if s.get("html") is not None]

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={"width": SLIDE_WIDTH, "height": SLIDE_HEIGHT},
        )

        for slide in html_slides:
            page = context.new_page()
            with tempfile.NamedTemporaryFile(
                suffix=".html", mode="w", encoding="utf-8", delete=False
            ) as f:
                f.write(slide["html"])
                tmp_path = f.name

            try:
                page.goto(
                    f"file:///{tmp_path.replace(os.sep, '/')}",
                    wait_until="load",
                )
                page.wait_for_timeout(1500)
                png_path = out_dir / f"slide_{slide['index']:02d}.png"
                page.screenshot(
                    path=str(png_path),
                    clip={"x": 0, "y": 0, "width": SLIDE_WIDTH, "height": SLIDE_HEIGHT},
                )
                indexed_paths.append((slide["index"], str(png_path)))
            finally:
                page.close()
                os.unlink(tmp_path)

        browser.close()

    # ── Image-based slides via Pillow ─────────────────────────────────────────
    for slide in slides:
        if slide.get("type") == "cta_image":
            png_path = out_dir / f"slide_{slide['index']:02d}.png"
            _render_cta_image(slide, png_path)
            indexed_paths.append((slide["index"], str(png_path)))

    indexed_paths.sort(key=lambda x: x[0])
    png_paths = [p for _, p in indexed_paths]

    pdf_path = _build_pdf(png_paths, out_dir, carousel_id)

    return {
        "carousel_id": carousel_id,
        "output_dir": str(out_dir),
        "png_paths": png_paths,
        "pdf_path": str(pdf_path),
        "slide_count": len(png_paths),
    }


async def render_slides(slides: list[dict], carousel_id: str | None = None) -> dict:
    if carousel_id is None:
        carousel_id = uuid.uuid4().hex
    return await asyncio.to_thread(_render_slides_sync, slides, carousel_id)


def _build_pdf(png_paths: list[str], out_dir: Path, carousel_id: str) -> Path:
    images = [Image.open(p).convert("RGB") for p in png_paths]
    pdf_path = out_dir / f"{carousel_id}.pdf"
    if images:
        images[0].save(
            str(pdf_path),
            save_all=True,
            append_images=images[1:],
            resolution=150,
        )
    return pdf_path
