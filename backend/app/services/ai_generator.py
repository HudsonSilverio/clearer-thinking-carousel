import os
import re
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

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


def _strip(text: str) -> str:
    return _EMOJI_RE.sub("", text).strip()


def _fallback(title: str) -> dict:
    return {
        "caption": f"{title[:150]}. Read more at clearerthinking.org",
        "hashtags": [
            "#ClearerThinking", "#Rationality", "#DecisionMaking",
            "#CriticalThinking", "#Cognition", "#Psychology",
            "#MentalModels", "#BehavioralScience", "#Learning", "#Growth",
        ],
    }


async def generate_content(title: str, takeaways: list[dict]) -> dict:
    """Generate Instagram caption and hashtags for a blog post.

    takeaways: list of {headline, body} dicts from the scraper.
    """
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key or api_key == "your_gemini_api_key_here":
        return _fallback(title)

    try:
        client = genai.Client(api_key=api_key)

        takeaway_block = "\n".join(
            f"- {t['headline']} {t.get('body', '')}".strip()
            for t in takeaways
        )

        prompt = f"""You are a social-media copywriter for the Clearer Thinking blog (clearerthinking.org).
Given this blog post, generate carousel content in JSON. No emojis anywhere.

Blog title: {title}

Key takeaways:
{takeaway_block}

Return ONLY valid JSON (no markdown fences) with exactly these keys:
{{
  "caption": "<Instagram caption, professional tone, under 200 characters, no emojis>",
  "hashtags": ["#ClearerThinking", "<9 more relevant hashtags>"]
}}"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.7),
        )
        raw = response.text.strip()
        raw = re.sub(r"^```[a-z]*\n?", "", raw).rstrip("`").strip()
        data = json.loads(raw)

        data["caption"] = _strip(data.get("caption", ""))[:200]
        data["hashtags"] = [_strip(h) for h in data.get("hashtags", [])]

        tags = data["hashtags"]
        ct = "#ClearerThinking"
        tags = [t for t in tags if t.lower() != ct.lower()]
        data["hashtags"] = [ct] + tags[:9]

        return data

    except Exception:
        return _fallback(title)
