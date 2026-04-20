import os
import uuid
import tempfile
from pathlib import Path
from playwright.async_api import async_playwright
import PIL.JpegImagePlugin  # registers JPEG encoder required by Pillow's PDF plugin
from PIL import Image
from app.utils.brand import SLIDE_WIDTH, SLIDE_HEIGHT

OUTPUT_DIR = Path(__file__).resolve().parents[4] / "generated_carousels"


async def render_slides(slides: list[dict], carousel_id: str | None = None) -> dict:
    if carousel_id is None:
        carousel_id = uuid.uuid4().hex

    out_dir = OUTPUT_DIR / carousel_id
    out_dir.mkdir(parents=True, exist_ok=True)

    png_paths: list[str] = []

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(
            viewport={"width": SLIDE_WIDTH, "height": SLIDE_HEIGHT},
        )

        for slide in slides:
            page = await context.new_page()

            # Write HTML to a temp file and load as file:// URL
            with tempfile.NamedTemporaryFile(
                suffix=".html", mode="w", encoding="utf-8", delete=False
            ) as f:
                f.write(slide["html"])
                tmp_path = f.name

            try:
                await page.goto(f"file:///{tmp_path.replace(os.sep, '/')}", wait_until="load")
                # Wait for Google Fonts to load
                await page.wait_for_timeout(1500)

                png_path = out_dir / f"slide_{slide['index']:02d}.png"
                await page.screenshot(
                    path=str(png_path),
                    clip={"x": 0, "y": 0, "width": SLIDE_WIDTH, "height": SLIDE_HEIGHT},
                )
                png_paths.append(str(png_path))
            finally:
                await page.close()
                os.unlink(tmp_path)

        await browser.close()

    pdf_path = _build_pdf(png_paths, out_dir, carousel_id)

    return {
        "carousel_id": carousel_id,
        "output_dir": str(out_dir),
        "png_paths": png_paths,
        "pdf_path": str(pdf_path),
        "slide_count": len(png_paths),
    }


def _build_pdf(png_paths: list[str], out_dir: Path, carousel_id: str) -> Path:
    images = []
    for p in png_paths:
        img = Image.open(p).convert("RGB")
        images.append(img)

    pdf_path = out_dir / f"{carousel_id}.pdf"
    if images:
        images[0].save(
            str(pdf_path),
            save_all=True,
            append_images=images[1:],
            resolution=150,
        )
    return pdf_path
