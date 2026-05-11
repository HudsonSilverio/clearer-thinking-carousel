"""
Standalone scraper worker — runs in its own process to avoid
Windows asyncio event-loop issues when called from uvicorn.

Usage:  python _scraper_worker.py <url>
Prints JSON result to stdout.
"""
import re
import sys
import json
from playwright.sync_api import sync_playwright

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
    cleaned = strip_emojis(text).strip()
    dot = cleaned.find(".")
    if dot != -1 and dot < len(cleaned) - 1:
        headline = cleaned[: dot + 1].strip()
        body = cleaned[dot + 1 :].strip()
    else:
        headline = cleaned
        body = ""
    return {"headline": headline, "body": body}


def _build_takeaway(headline_line: str, body_lines: list[str]) -> dict:
    parsed = _split_takeaway(headline_line)
    inline_body = parsed.get("body", "")
    collected = " ".join(body_lines).strip()
    if len(inline_body) > 50 or not collected:
        return {"headline": parsed["headline"], "body": inline_body}
    final_body = f"{inline_body} {collected}".strip() if inline_body else collected
    return {"headline": parsed["headline"], "body": final_body}


def _extract_title(page) -> str:
    h1s = page.query_selector_all("h1")
    for h in h1s:
        text = h.inner_text().strip()
        if text:
            return strip_emojis(text)
    raw = page.title()
    return strip_emojis(raw.split("|")[0].strip())


def _extract_cover_image(page) -> str | None:
    imgs = page.query_selector_all("img[src*='wixstatic']")
    for img in imgs:
        src = img.get_attribute("src") or ""
        if _SITE_BANNER_ID in src:
            continue
        nat_w = img.evaluate("el => el.naturalWidth")
        if nat_w > 200:
            base = src.split("/v1/")[0]
            return f"{base}/v1/fill/w_1200,h_630,al_c,q_90,usm_0.66_1.00_0.01/image.png"
    return None


def _extract_takeaways(page) -> list[dict]:
    body_text = page.inner_text("body")
    lines = [l.strip() for l in body_text.splitlines() if l.strip()]

    takeaway_start = None
    for i, line in enumerate(lines):
        if "key takeaway" in line.lower():
            takeaway_start = i + 1
            break

    if takeaway_start is None:
        for i, line in enumerate(lines):
            if _EMOJI_RE.match(line):
                run = sum(1 for l in lines[i : i + 5] if _EMOJI_RE.match(l))
                if run >= 3:
                    takeaway_start = i
                    break

    if takeaway_start is None:
        return []

    MAX_BODY = 5
    MAX_GAP = 12

    active_headline = None
    active_body = []
    gap = 0
    groups = []

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


def scrape_post(url: str) -> dict:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=45_000)
        page.wait_for_timeout(2_000)

        title = _extract_title(page)
        cover_image = _extract_cover_image(page)
        takeaways = _extract_takeaways(page)

        browser.close()

    return {
        "url": url,
        "title": title,
        "cover_image": cover_image,
        "takeaways": takeaways,
        "takeaway_count": len(takeaways),
    }


if __name__ == "__main__":
    url = sys.argv[1]
    result = scrape_post(url)
    print(json.dumps(result, ensure_ascii=False))
