import re
from playwright.async_api import async_playwright

_SITE_BANNER_ID = "a8e1f3e15ccb41b88df85a10bb90531a"

_EMOJI_RE = re.compile(
    "["
    "\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\U00002600-\U000027BF"
    "\U0001F900-\U0001F9FF"
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "\U0001FA00-\U0001FA6F"
    "\U0001FA70-\U0001FAFF"
    "]+",
    flags=re.UNICODE,
)


def strip_emojis(text: str) -> str:
    return _EMOJI_RE.sub("", text).strip()


def _split_takeaway(text: str) -> dict:
    """Split 'Headline sentence. Body explanation text.' into {headline, body}."""
    cleaned = strip_emojis(text).strip()
    dot = cleaned.find(".")
    if dot != -1 and dot < len(cleaned) - 1:
        headline = cleaned[: dot + 1].strip()
        body = cleaned[dot + 1 :].strip()
    else:
        headline = cleaned  # keep as-is (period at end or no period)
        body = ""
    return {"headline": headline, "body": body}


def _build_takeaway(headline_line: str, body_lines: list[str]) -> dict:
    """Merge an emoji-prefixed headline line with optional collected body lines."""
    parsed = _split_takeaway(headline_line)
    inline_body = parsed.get("body", "")
    collected = " ".join(body_lines).strip()
    # If the emoji line already has substantial inline body, use it as-is
    if len(inline_body) > 50 or not collected:
        return {"headline": parsed["headline"], "body": inline_body}
    # Otherwise merge: inline prefix (if any) + collected body lines
    final_body = f"{inline_body} {collected}".strip() if inline_body else collected
    return {"headline": parsed["headline"], "body": final_body}


async def scrape_post(url: str) -> dict:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=45_000)
        await page.wait_for_timeout(5_000)

        title = await _extract_title(page)
        cover_image = await _extract_cover_image(page)
        takeaways = await _extract_takeaways(page)

        await browser.close()

    return {
        "url": url,
        "title": title,
        "cover_image": cover_image,
        "takeaways": takeaways,
        "takeaway_count": len(takeaways),
    }


async def _extract_title(page) -> str:
    h1s = await page.query_selector_all("h1")
    for h in h1s:
        text = (await h.inner_text()).strip()
        if text:
            return strip_emojis(text)
    raw = await page.title()
    return strip_emojis(raw.split("|")[0].strip())


async def _extract_cover_image(page) -> str | None:
    imgs = await page.query_selector_all("img[src*='wixstatic']")
    for img in imgs:
        src = await img.get_attribute("src") or ""
        if _SITE_BANNER_ID in src:
            continue
        nat_w = await img.evaluate("el => el.naturalWidth")
        if nat_w > 200:
            base = src.split("/v1/")[0]
            return f"{base}/v1/fill/w_1200,h_630,al_c,q_90,usm_0.66_1.00_0.01/image.png"
    return None


async def _extract_takeaways(page) -> list[dict]:
    body_text = await page.inner_text("body")
    lines = [l.strip() for l in body_text.splitlines() if l.strip()]

    # Strategy 1: look for explicit "key takeaways" marker
    takeaway_start = None
    for i, line in enumerate(lines):
        if "key takeaway" in line.lower():
            takeaway_start = i + 1
            break

    # Strategy 2: first run of 3+ consecutive emoji-prefixed lines
    if takeaway_start is None:
        for i, line in enumerate(lines):
            if _EMOJI_RE.match(line):
                run = sum(1 for l in lines[i : i + 5] if _EMOJI_RE.match(l))
                if run >= 3:
                    takeaway_start = i
                    break

    if takeaway_start is None:
        return []

    # Group lines into takeaways.  Each group starts with an emoji-prefixed
    # line (headline); non-emoji lines that follow are the body.  Stop scanning
    # after MAX_GAP consecutive non-emoji lines (the takeaway section has ended).
    MAX_BODY = 5
    MAX_GAP = 12

    active_headline: str | None = None
    active_body: list[str] = []
    gap = 0
    groups: list[tuple[str, list[str]]] = []

    for line in lines[takeaway_start:]:
        if _EMOJI_RE.match(line):
            if active_headline is not None:
                groups.append((active_headline, active_body))
            active_headline = line
            active_body = []
            gap = 0
        else:
            gap += 1
            if gap > MAX_GAP:
                break
            if active_headline is not None and len(active_body) < MAX_BODY:
                active_body.append(line)

    if active_headline is not None:
        groups.append((active_headline, active_body))

    return [t for t in (_build_takeaway(hl, b) for hl, b in groups) if t["headline"]]
