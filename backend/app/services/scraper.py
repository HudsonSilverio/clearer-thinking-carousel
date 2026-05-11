import re
import sys
import json
import asyncio
import subprocess
from pathlib import Path

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

_WORKER_SCRIPT = Path(__file__).with_name("_scraper_worker.py")


def strip_emojis(text: str) -> str:
    return _EMOJI_RE.sub("", text).strip()


async def scrape_post(url: str) -> dict:
    """Run scraper in a separate process to avoid Windows event-loop issues."""
    import logging
    logger = logging.getLogger(__name__)
    worker = str(_WORKER_SCRIPT)
    logger.info(f"scrape_post: worker={worker}, exists={_WORKER_SCRIPT.exists()}")
    try:
        proc = await asyncio.to_thread(
            subprocess.run,
            [sys.executable, worker, url],
            capture_output=True,
            text=True,
            timeout=90,
        )
        logger.info(f"scrape_post: rc={proc.returncode}, stdout_len={len(proc.stdout)}, stderr_len={len(proc.stderr)}")
        if proc.returncode != 0:
            logger.error(f"scrape_post stderr: {proc.stderr}")
            raise RuntimeError(proc.stderr or "Scraper process failed")
        return json.loads(proc.stdout)
    except Exception as e:
        logger.error(f"scrape_post exception: {type(e).__name__}: {e}")
        raise
