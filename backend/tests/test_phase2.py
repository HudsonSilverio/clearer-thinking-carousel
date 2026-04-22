import re
import pytest
from app.services.scraper import scrape_post
from app.services.ai_generator import generate_content
from app.services.carousel_builder import build_slides
from app.services.image_renderer import render_slides

TEST_URL = "https://www.clearerthinking.org/post/whats-scaring-people-about-ai-we-ran-a-study-to-find-out"

_EMOJI_RE = re.compile(
    "["
    "\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF\U00002600-\U000027BF\U0001F900-\U0001F9FF"
    "\U00002702-\U000027B0\U000024C2-\U0001F251"
    "\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF"
    "]+",
    flags=re.UNICODE,
)


def _has_emoji(text: str) -> bool:
    return bool(_EMOJI_RE.search(text))


@pytest.mark.asyncio
async def test_ai_generator():
    scraped = await scrape_post(TEST_URL)
    title = scraped["title"]
    takeaways = scraped["takeaways"]
    assert takeaways, "No takeaways scraped — cannot test AI generator"

    ai = await generate_content(title, takeaways)

    assert ai.get("caption"), "caption is missing"
    assert ai.get("hashtags"), "hashtags is missing"
    assert ai["hashtags"][0] == "#ClearerThinking", (
        f"First hashtag must be #ClearerThinking, got {ai['hashtags'][0]}"
    )
    assert not _has_emoji(ai["caption"]), f"Emoji in caption: {ai['caption']!r}"


@pytest.mark.asyncio
async def test_carousel_builder():
    scraped = await scrape_post(TEST_URL)

    slides = build_slides(
        title=scraped["title"],
        cover_image=scraped["cover_image"],
        takeaways=scraped["takeaways"],
    )

    expected_count = len(scraped["takeaways"]) + 2
    assert len(slides) == expected_count, (
        f"Expected {expected_count} slides, got {len(slides)}"
    )
    assert slides[0]["type"] == "cover", "First slide must be cover"
    assert slides[-1]["type"] == "cta", "Last slide must be cta"

    for s in slides[1:-1]:
        assert s["type"] == "content", f"Middle slide {s['index']} must be content"

    for s in slides:
        assert "1080" in s["html"], f"Slide {s['index']} HTML missing '1080'"
    assert scraped["title"] in slides[0]["html"], "Cover slide must contain the blog title"

    # Content slides must include headline text from scraped takeaways
    for i, t in enumerate(scraped["takeaways"]):
        assert t["headline"] in slides[i + 1]["html"], (
            f"Slide {i + 1} missing headline: {t['headline']!r}"
        )


@pytest.mark.asyncio
async def test_image_renderer():
    scraped = await scrape_post(TEST_URL)
    slides = build_slides(
        title=scraped["title"],
        cover_image=scraped["cover_image"],
        takeaways=scraped["takeaways"],
    )

    rendered = await render_slides(slides)

    assert rendered["slide_count"] == len(slides), "PNG count mismatch"

    from pathlib import Path
    for png in rendered["png_paths"]:
        p = Path(png)
        assert p.exists(), f"PNG missing: {png}"
        assert p.stat().st_size > 1000, f"PNG too small: {png}"

    pdf = Path(rendered["pdf_path"])
    assert pdf.exists(), "PDF missing"
    assert pdf.stat().st_size > 5000, f"PDF too small: {pdf.stat().st_size} bytes"
