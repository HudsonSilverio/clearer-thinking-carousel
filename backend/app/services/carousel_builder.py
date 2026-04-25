import base64
import html as html_mod
import mimetypes
from pathlib import Path
from app.utils.brand import (
    SLIDE_WIDTH, SLIDE_HEIGHT,
    SLIDE_BG, COVER_BG, TEXT_HEADLINE, TEXT_BODY,
    PROGRESS_BAR_COLOR,
)

_SITE_ROOT = Path(__file__).resolve().parents[3]  # clearer-thinking-carousel/
CTA_IMAGE_PATH = _SITE_ROOT / "dashboard" / "public" / "cta-slide.png"

# ─── Font registry ────────────────────────────────────────────────────────────

_FONT_GF_PARAMS = {
    "Plus Jakarta Sans": "Plus+Jakarta+Sans:wght@400;500;600",
    "DM Sans":           "DM+Sans:wght@400;500",
    "Source Serif 4":    "Source+Serif+4:ital,wght@0,400;0,500;1,400",
    "Inter":             "Inter:wght@400;500;600",
    "Lora":              "Lora:ital,wght@0,400;0,500;1,400",
    "Merriweather":      "Merriweather:wght@400;700",
    "Roboto":            "Roboto:wght@400;500",
    "Open Sans":         "Open+Sans:wght@400;500;600",
}

_FONT_STACK = {
    "Plus Jakarta Sans": "'Plus Jakarta Sans', sans-serif",
    "DM Sans":           "'DM Sans', sans-serif",
    "Source Serif 4":    "'Source Serif 4', serif",
    "Inter":             "'Inter', sans-serif",
    "Lora":              "'Lora', serif",
    "Merriweather":      "'Merriweather', serif",
    "Roboto":            "'Roboto', sans-serif",
    "Open Sans":         "'Open Sans', sans-serif",
}

_DEFAULT_TYPOGRAPHY = {
    "headline_font": "Source Serif 4",
    "body_font":     "Plus Jakarta Sans",
    "headline_size": 42,
    "body_size":     28,
    "text_align":    "left",
}

_DEFAULT_COLORS = {
    "slide_bg":     SLIDE_BG,
    "headline":     TEXT_HEADLINE,
    "body":         TEXT_BODY,
    "progress_bar": PROGRESS_BAR_COLOR,
}

_BASE_CSS = f"""
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    width: {SLIDE_WIDTH}px;
    height: {SLIDE_HEIGHT}px;
    overflow: hidden;
    -webkit-font-smoothing: antialiased;
}}
.slide {{
    width: {SLIDE_WIDTH}px;
    height: {SLIDE_HEIGHT}px;
    position: relative;
    overflow: hidden;
}}
"""

# ─── Helpers ─────────────────────────────────────────────────────────────────

def _resolve_colors(overrides: dict | None) -> dict:
    c = dict(_DEFAULT_COLORS)
    if overrides:
        c.update({k: v for k, v in overrides.items() if v})
    return c


def _resolve_typography(overrides: dict | None) -> dict:
    t = dict(_DEFAULT_TYPOGRAPHY)
    if overrides:
        t.update({k: v for k, v in overrides.items() if v is not None})
    return t


def _fonts_html(headline_font: str, body_font: str) -> str:
    needed = {headline_font, body_font}
    params = "&".join(
        f"family={_FONT_GF_PARAMS[f]}"
        for f in needed
        if f in _FONT_GF_PARAMS
    )
    if not params:
        return ""
    url = f"https://fonts.googleapis.com/css2?{params}&display=swap"
    return (
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        f'<link href="{url}" rel="stylesheet">'
    )


def _head(headline_font: str = "Source Serif 4", body_font: str = "Plus Jakarta Sans") -> str:
    return (
        f'<!DOCTYPE html><html><head><meta charset="utf-8">\n'
        f'{_fonts_html(headline_font, body_font)}\n'
        f'<style>{_BASE_CSS}</style>\n'
        f'</head><body>'
    )


def _esc(text: str) -> str:
    return html_mod.escape(str(text))


def _img_src(path_or_url: str) -> str:
    """Convert a local file path to a data-URL; leave remote URLs untouched."""
    if not path_or_url:
        return ""
    if path_or_url.startswith("http") or path_or_url.startswith("data:"):
        return path_or_url
    try:
        p = Path(path_or_url)
        if p.exists():
            mt = mimetypes.guess_type(str(p))[0] or "image/jpeg"
            return f"data:{mt};base64,{base64.b64encode(p.read_bytes()).decode()}"
    except Exception:
        pass
    return path_or_url


def _progress_bar(index: int, total: int, color: str) -> str:
    pct = round((index + 1) / total * 100, 2)
    return (
        f'<div style="position:absolute;bottom:0;left:0;'
        f'width:{pct}%;height:8px;background:{color};"></div>'
    )

# ─── Slide builders ───────────────────────────────────────────────────────────

def build_cover_slide(title: str, cover_image: str | None, colors: dict, typography: dict) -> str:
    hf  = _FONT_STACK.get(typography["headline_font"], "'Source Serif 4', serif")
    hs  = typography["headline_size"]
    top = round(SLIDE_HEIGHT * 0.65)
    bot = SLIDE_HEIGHT - top

    if cover_image:
        src = _img_src(cover_image)
        img_css = f"background:url('{src}') center/cover no-repeat;"
    else:
        img_css = f"background:{colors['slide_bg']};"

    return (
        f'{_head(typography["headline_font"], typography["body_font"])}\n'
        f'<div class="slide" style="display:flex;flex-direction:column;background:{COVER_BG};">\n'
        f'  <div style="width:{SLIDE_WIDTH}px;height:{top}px;flex-shrink:0;{img_css}"></div>\n'
        f'  <div style="width:{SLIDE_WIDTH}px;height:{bot}px;background:{COVER_BG};display:flex;\n'
        f'       flex-direction:column;align-items:center;justify-content:center;\n'
        f'       padding:40px 80px;flex-shrink:0;">\n'
        f'    <div style="font-family:{hf};font-size:{hs}px;font-weight:400;\n'
        f'         color:{colors["headline"]};text-align:center;line-height:1.3;\n'
        f'         margin-bottom:24px;">{_esc(title)}</div>\n'
        f'    <div style="width:40px;height:4px;background:{colors["progress_bar"]};\n'
        f'         border-radius:2px;"></div>\n'
        f'  </div>\n'
        f'</div>\n</body></html>'
    )


def build_content_slide(
    headline: str,
    body: str,
    index: int,
    total: int,
    colors: dict,
    typography: dict,
    slide_image: str | None = None,
) -> str:
    hf  = _FONT_STACK.get(typography["headline_font"], "'Source Serif 4', serif")
    bf  = _FONT_STACK.get(typography["body_font"],    "'Plus Jakarta Sans', sans-serif")
    hs  = typography["headline_size"]
    bs  = typography["body_size"]
    ta  = typography.get("text_align", "left")
    pad = 55

    img_html = ""
    if slide_image:
        src = _img_src(slide_image)
        img_html = (
            f'<div style="margin-top:28px;">'
            f'<img src="{src}" style="width:100%;max-height:260px;'
            f'object-fit:cover;border-radius:12px;display:block;"/>'
            f'</div>'
        )

    return (
        f'{_head(typography["headline_font"], typography["body_font"])}\n'
        f'<div class="slide" style="background:{colors["slide_bg"]};">\n'
        f'  <div style="padding:70px {pad}px 0 {pad}px;">\n'
        f'    <div style="font-family:{hf};font-size:{hs}px;font-weight:500;\n'
        f'         color:{colors["headline"]};line-height:1.25;margin-bottom:28px;\n'
        f'         text-align:{ta};">'
        f'{_esc(headline)}</div>\n'
        f'    <div style="font-family:{bf};font-size:{bs}px;font-weight:400;\n'
        f'         color:{colors["body"]};line-height:1.45;\n'
        f'         text-align:{ta};">{_esc(body)}</div>\n'
        f'    {img_html}\n'
        f'  </div>\n'
        f'  {_progress_bar(index, total, colors["progress_bar"])}\n'
        f'</div>\n</body></html>'
    )


def build_slides(
    title: str,
    cover_image: str | None,
    takeaways: list[dict],
    colors: dict | None = None,
    typography: dict | None = None,
) -> list[dict]:
    """Build all slides.

    takeaways: list of {headline, body, slide_image?} dicts.
    Returns a mix of HTML slides and a cta_image descriptor for the last slide.
    """
    c = _resolve_colors(colors)
    t = _resolve_typography(typography)
    total = len(takeaways) + 2

    slides = [{"type": "cover", "index": 0, "html": build_cover_slide(title, cover_image, c, t)}]

    for i, takeaway in enumerate(takeaways):
        slides.append({
            "type": "content",
            "index": i + 1,
            "html": build_content_slide(
                takeaway["headline"],
                takeaway.get("body", ""),
                i + 1,
                total,
                c,
                t,
                takeaway.get("slide_image"),
            ),
        })

    # CTA: fixed owl image rendered by Pillow, not Playwright
    slides.append({
        "type": "cta_image",
        "index": total - 1,
        "html": None,
        "cta_image_path": str(CTA_IMAGE_PATH),
        "progress_bar_color": c["progress_bar"],
    })

    return slides
