import html as html_mod
from app.utils.brand import (
    SLIDE_WIDTH, SLIDE_HEIGHT,
    SLIDE_BG, COVER_BG, TEXT_HEADLINE, TEXT_BODY,
    PROGRESS_BAR_COLOR, ACCENT_BLUE,
)

_FONTS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,wght@0,400;0,500;1,400&family=Plus+Jakarta+Sans:wght@400;500;600&display=swap" rel="stylesheet">
"""

_BASE_CSS = f"""
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
    width: {SLIDE_WIDTH}px;
    height: {SLIDE_HEIGHT}px;
    overflow: hidden;
    font-family: 'Plus Jakarta Sans', sans-serif;
    -webkit-font-smoothing: antialiased;
}}
.slide {{
    width: {SLIDE_WIDTH}px;
    height: {SLIDE_HEIGHT}px;
    position: relative;
    overflow: hidden;
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


def _progress_bar(index: int, total: int) -> str:
    pct = round((index + 1) / total * 100, 2)
    return f"""
    <div style="
        position: absolute;
        bottom: 0; left: 0;
        width: {pct}%;
        height: 8px;
        background: {PROGRESS_BAR_COLOR};
    "></div>"""


def build_cover_slide(title: str, cover_image: str | None) -> str:
    cover_top_h = round(SLIDE_HEIGHT * 0.65)   # 702px
    cover_bot_h = SLIDE_HEIGHT - cover_top_h   # 378px

    if cover_image:
        img_section = f"""
        <div style="
            width: {SLIDE_WIDTH}px;
            height: {cover_top_h}px;
            background: url('{cover_image}') center/cover no-repeat;
            flex-shrink: 0;
        "></div>"""
    else:
        img_section = f"""
        <div style="
            width: {SLIDE_WIDTH}px;
            height: {cover_top_h}px;
            background: {SLIDE_BG};
            flex-shrink: 0;
        "></div>"""

    extra_css = ""
    return f"""{_head(extra_css)}
<div class="slide" style="display: flex; flex-direction: column; background: {COVER_BG};">
    {img_section}
    <div style="
        width: {SLIDE_WIDTH}px;
        height: {cover_bot_h}px;
        background: {COVER_BG};
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 40px 80px;
        flex-shrink: 0;
    ">
        <div style="
            font-family: 'Source Serif 4', serif;
            font-size: 40px;
            font-weight: 400;
            color: {TEXT_HEADLINE};
            text-align: center;
            line-height: 1.3;
            margin-bottom: 24px;
        ">{_esc(title)}</div>
        <div style="
            width: 40px;
            height: 4px;
            background: {PROGRESS_BAR_COLOR};
            border-radius: 2px;
        "></div>
    </div>
</div>
</body></html>"""


def build_content_slide(headline: str, body: str, index: int, total: int) -> str:
    pad = 65
    return f"""{_head()}
<div class="slide" style="background: {SLIDE_BG};">
    <div style="
        padding: {pad}px {pad}px 0 {pad}px;
        padding-top: 120px;
    ">
        <div style="
            font-family: 'Source Serif 4', serif;
            font-size: 38px;
            font-weight: 500;
            color: {TEXT_HEADLINE};
            line-height: 1.3;
            margin-bottom: 40px;
        ">{_esc(headline)}</div>
        <div style="
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 23px;
            font-weight: 400;
            color: {TEXT_BODY};
            line-height: 1.65;
        ">{_esc(body)}</div>
    </div>
    {_progress_bar(index, total)}
</div>
</body></html>"""


def build_cta_slide(index: int, total: int) -> str:
    return f"""{_head()}
<div class="slide" style="background: {SLIDE_BG}; display: flex; flex-direction: column; align-items: center; justify-content: center;">
    <div style="
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
        padding: 0 100px;
        gap: 56px;
    ">
        <div style="
            font-family: 'Source Serif 4', serif;
            font-size: 32px;
            font-weight: 400;
            color: {TEXT_HEADLINE};
            line-height: 1.4;
            max-width: 700px;
        ">Read the full article (or listen to it) on our website</div>

        <div style="display: flex; align-items: center; gap: 28px;">
            <div style="
                width: 0; height: 0;
                border-top: 16px solid transparent;
                border-bottom: 16px solid transparent;
                border-left: 24px solid {ACCENT_BLUE};
                opacity: 0.7;
            "></div>

            <div style="
                background: #FFFFFF;
                border-radius: 20px;
                box-shadow: 0 4px 24px rgba(0,0,0,0.10);
                padding: 28px 48px;
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 10px;
            ">
                <div style="font-size: 36px;">&#x1F50D;</div>
                <div style="
                    font-family: 'Plus Jakarta Sans', sans-serif;
                    font-size: 22px;
                    font-weight: 600;
                    color: {TEXT_HEADLINE};
                ">ClearerThinking.org</div>
            </div>

            <div style="
                width: 0; height: 0;
                border-top: 16px solid transparent;
                border-bottom: 16px solid transparent;
                border-right: 24px solid {ACCENT_BLUE};
                opacity: 0.7;
            "></div>
        </div>

        <div style="
            font-family: 'Plus Jakarta Sans', sans-serif;
            font-size: 20px;
            font-weight: 400;
            color: {TEXT_BODY};
            font-style: italic;
        ">www.clearerthinking.org/blog</div>
    </div>

    {_progress_bar(index, total)}
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

    slides.append({
        "type": "cover",
        "index": 0,
        "html": build_cover_slide(title, cover_image),
    })

    for i, (takeaway, headline) in enumerate(zip(takeaways, slide_headlines)):
        slides.append({
            "type": "content",
            "index": i + 1,
            "html": build_content_slide(headline, takeaway, i + 1, total),
        })

    slides.append({
        "type": "cta",
        "index": total - 1,
        "html": build_cta_slide(total - 1, total),
    })

    return slides
