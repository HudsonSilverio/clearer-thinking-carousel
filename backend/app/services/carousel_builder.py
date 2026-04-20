import html as html_mod
from app.utils.brand import BRAND_PRIMARY, BRAND_ACCENT, BRAND_DARK_BG, SLIDE_WIDTH, SLIDE_HEIGHT, IG_HANDLE

_FONTS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Plus+Jakarta+Sans:wght@700;800&display=swap" rel="stylesheet">
"""

_BASE_CSS = f"""
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    width: {SLIDE_WIDTH}px;
    height: {SLIDE_HEIGHT}px;
    overflow: hidden;
    font-family: 'DM Sans', sans-serif;
}}
.slide {{
    width: {SLIDE_WIDTH}px;
    height: {SLIDE_HEIGHT}px;
    position: relative;
    overflow: hidden;
    display: flex;
    flex-direction: column;
}}
.content {{
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 80px;
    position: relative;
    z-index: 2;
}}
.brand-strip {{
    height: 72px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 80px;
    position: relative;
    z-index: 2;
    flex-shrink: 0;
}}
.brand-handle {{
    font-family: 'DM Sans', sans-serif;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 0.5px;
}}
.progress {{
    font-family: 'DM Sans', sans-serif;
    font-size: 16px;
    font-weight: 500;
    opacity: 0.7;
}}
"""


def _head(extra_css: str = "") -> str:
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
{_FONTS}
<style>
{_BASE_CSS}
{extra_css}
</style>
</head>
<body>"""


def _esc(text: str) -> str:
    return html_mod.escape(str(text))


def _truncate(text: str, limit: int = 280) -> str:
    return text if len(text) <= limit else text[:limit - 1] + "…"


def build_cover_slide(title: str, hook: str, cover_image: str | None, index: int, total: int) -> str:
    img_css = ""
    if cover_image:
        img_css = f"""
.bg-img {{
    position: absolute; inset: 0; z-index: 0;
    background: url('{cover_image}') center/cover no-repeat;
}}
.overlay {{
    position: absolute; inset: 0; z-index: 1;
    background: linear-gradient(160deg, rgba(26,26,46,0.85) 0%, rgba(26,26,46,0.95) 100%);
}}"""
    else:
        img_css = f"""
.bg-img {{ position: absolute; inset: 0; z-index: 0; background: {BRAND_DARK_BG}; }}
.overlay {{ display: none; }}"""

    extra_css = img_css + f"""
.hook {{
    font-family: 'DM Sans', sans-serif;
    font-size: 20px;
    font-weight: 500;
    color: {BRAND_PRIMARY};
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 28px;
}}
.title {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 54px;
    font-weight: 800;
    color: #FFFFFF;
    line-height: 1.15;
    margin-bottom: 48px;
}}
.accent-line {{
    width: 64px; height: 6px;
    background: {BRAND_PRIMARY};
    border-radius: 3px;
    margin-bottom: 28px;
}}
"""

    body_bg = "" if cover_image else f"background:{BRAND_DARK_BG};"
    return f"""{_head(extra_css)}
<div class="slide" style="{body_bg}">
  <div class="bg-img"></div>
  <div class="overlay"></div>
  <div class="content" style="justify-content:flex-end; padding-bottom:40px;">
    <div class="accent-line"></div>
    <div class="hook">{_esc(hook)}</div>
    <div class="title">{_esc(title)}</div>
  </div>
  <div class="brand-strip" style="background:rgba(0,0,0,0.4);">
    <span class="brand-handle" style="color:{BRAND_PRIMARY};">{_esc(IG_HANDLE)}</span>
    <span class="progress" style="color:#fff;">{index + 1}/{total}</span>
  </div>
</div>
</body></html>"""


def build_content_slide(headline: str, body: str, takeaway_num: int, index: int, total: int) -> str:
    is_dark = (index % 2 == 1)
    bg = BRAND_DARK_BG if is_dark else BRAND_ACCENT
    text_color = "#FFFFFF"
    label_color = BRAND_PRIMARY if is_dark else "rgba(255,255,255,0.6)"

    extra_css = f"""
.slide-bg {{ position: absolute; inset: 0; background: {bg}; z-index: 0; }}
.deco-num {{
    position: absolute;
    right: -20px; top: 50%;
    transform: translateY(-50%);
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 320px;
    font-weight: 800;
    color: rgba(255,255,255,0.04);
    line-height: 1;
    z-index: 1;
    user-select: none;
}}
.label {{
    font-family: 'DM Sans', sans-serif;
    font-size: 16px;
    font-weight: 700;
    letter-spacing: 3px;
    color: {label_color};
    text-transform: uppercase;
    margin-bottom: 20px;
}}
.accent-line {{
    width: 48px; height: 5px;
    background: {BRAND_PRIMARY};
    border-radius: 3px;
    margin-bottom: 32px;
}}
.headline {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 48px;
    font-weight: 800;
    color: {text_color};
    line-height: 1.2;
    margin-bottom: 32px;
}}
.body-text {{
    font-family: 'DM Sans', sans-serif;
    font-size: 22px;
    font-weight: 400;
    color: rgba(255,255,255,0.8);
    line-height: 1.6;
}}
"""
    return f"""{_head(extra_css)}
<div class="slide">
  <div class="slide-bg"></div>
  <div class="deco-num">{takeaway_num}</div>
  <div class="content" style="z-index:2;">
    <div class="label">Key Takeaway {takeaway_num}</div>
    <div class="accent-line"></div>
    <div class="headline">{_esc(headline)}</div>
    <div class="body-text">{_esc(_truncate(body))}</div>
  </div>
  <div class="brand-strip" style="background:rgba(0,0,0,0.2);">
    <span class="brand-handle" style="color:{BRAND_PRIMARY};">{_esc(IG_HANDLE)}</span>
    <span class="progress" style="color:rgba(255,255,255,0.7);">{index + 1}/{total}</span>
  </div>
</div>
</body></html>"""


def build_cta_slide(index: int, total: int) -> str:
    extra_css = f"""
.slide-bg {{
    position: absolute; inset: 0; z-index: 0;
    background: linear-gradient(135deg, {BRAND_PRIMARY} 0%, {BRAND_ACCENT} 100%);
}}
.cta-content {{
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 80px;
    z-index: 2;
    text-align: center;
}}
.cta-label {{
    font-family: 'DM Sans', sans-serif;
    font-size: 18px;
    font-weight: 700;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.7);
    margin-bottom: 28px;
}}
.cta-heading {{
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 60px;
    font-weight: 800;
    color: #FFFFFF;
    line-height: 1.15;
    margin-bottom: 40px;
}}
.cta-btn {{
    background: #FFFFFF;
    color: {BRAND_PRIMARY};
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 22px;
    font-weight: 800;
    padding: 20px 56px;
    border-radius: 50px;
    margin-bottom: 36px;
    display: inline-block;
}}
.cta-url {{
    font-family: 'DM Sans', sans-serif;
    font-size: 20px;
    color: rgba(255,255,255,0.8);
    letter-spacing: 0.5px;
}}
"""
    return f"""{_head(extra_css)}
<div class="slide">
  <div class="slide-bg"></div>
  <div class="cta-content">
    <div class="cta-label">Want to go deeper?</div>
    <div class="cta-heading">Read the Full Article</div>
    <div class="cta-btn">Read Now</div>
    <div class="cta-url">clearerthinking.org/blog</div>
  </div>
  <div class="brand-strip" style="background:rgba(0,0,0,0.15);">
    <span class="brand-handle" style="color:#fff; opacity:0.9;">{_esc(IG_HANDLE)}</span>
    <span class="progress" style="color:rgba(255,255,255,0.7);">{index + 1}/{total}</span>
  </div>
</div>
</body></html>"""


def build_slides(
    title: str,
    cover_image: str | None,
    takeaways: list[str],
    hook: str,
    slide_headlines: list[str],
) -> list[dict]:
    total = len(takeaways) + 2  # cover + content slides + CTA

    slides = []

    # Cover slide
    slides.append({
        "type": "cover",
        "index": 0,
        "html": build_cover_slide(title, hook, cover_image, 0, total),
    })

    # Content slides
    for i, (takeaway, headline) in enumerate(zip(takeaways, slide_headlines)):
        slides.append({
            "type": "content",
            "index": i + 1,
            "html": build_content_slide(headline, takeaway, i + 1, i + 1, total),
        })

    # CTA slide
    slides.append({
        "type": "cta",
        "index": total - 1,
        "html": build_cta_slide(total - 1, total),
    })

    return slides
