import pytest
from app.services.scraper import scrape_post, strip_emojis

TEST_URL = "https://www.clearerthinking.org/post/how-and-when-to-learn-from-crowds"


@pytest.mark.asyncio
async def test_scrape_returns_title():
    result = await scrape_post(TEST_URL)
    assert result["title"]
    assert "Crowds" in result["title"]


@pytest.mark.asyncio
async def test_scrape_returns_cover_image():
    result = await scrape_post(TEST_URL)
    assert result["cover_image"]
    assert result["cover_image"].startswith("https://static.wixstatic.com")


@pytest.mark.asyncio
async def test_scrape_returns_takeaways():
    result = await scrape_post(TEST_URL)
    takeaways = result["takeaways"]
    assert len(takeaways) >= 3


@pytest.mark.asyncio
async def test_takeaways_have_no_emojis():
    result = await scrape_post(TEST_URL)
    for t in result["takeaways"]:
        assert t == strip_emojis(t), f"Emoji found in: {t!r}"


@pytest.mark.asyncio
async def test_title_has_no_emojis():
    result = await scrape_post(TEST_URL)
    assert result["title"] == strip_emojis(result["title"])


def test_strip_emojis_removes_leading_emoji():
    assert strip_emojis("👥 Some text here") == "Some text here"


def test_strip_emojis_removes_multiple_emojis():
    assert strip_emojis("🎯⚠️ Mixed content") == "Mixed content"


def test_strip_emojis_leaves_plain_text_unchanged():
    text = "No emojis at all"
    assert strip_emojis(text) == text
