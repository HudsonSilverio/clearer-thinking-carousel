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


def _fallback(title: str, takeaways: list[str]) -> dict:
    headlines = []
    for t in takeaways:
        words = t.split()
        headlines.append(" ".join(words[:8]) if len(words) > 8 else t)

    caption = f"{title[:150]}. Read more at clearerthinking.org"
    return {
        "hook": title[:60],
        "slide_headlines": headlines,
        "caption": caption[:200],
        "hashtags": [
            "#ClearerThinking", "#Rationality", "#DecisionMaking",
            "#CriticalThinking", "#Cognition", "#Psychology",
            "#MentalModels", "#BehavioralScience", "#Learning", "#Growth",
        ],
    }


async def generate_content(title: str, takeaways: list[str]) -> dict:
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key or api_key == "your_gemini_api_key_here":
        return _fallback(title, takeaways)

    try:
        client = genai.Client(api_key=api_key)

        takeaway_block = "\n".join(f"- {t}" for t in takeaways)
        prompt = f"""You are a social-media copywriter for the Clearer Thinking blog (clearerthinking.org).
Given this blog post, generate carousel content in JSON. No emojis anywhere.

Blog title: {title}

Key takeaways:
{takeaway_block}

Return ONLY valid JSON (no markdown fences) with exactly these keys:
{{
  "hook": "<6-10 word compelling hook for the cover slide>",
  "slide_headlines": ["<5-10 word headline for each takeaway, same count as takeaways>"],
  "caption": "<Instagram caption, professional tone, under 200 characters>",
  "hashtags": ["#ClearerThinking", "<9 more relevant hashtags>"]
}}"""

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.7),
        )
        raw = response.text.strip()
        # Strip markdown code fences if present
        raw = re.sub(r"^```[a-z]*\n?", "", raw).rstrip("`").strip()
        data = json.loads(raw)

        # Sanitise every string field
        data["hook"] = _strip(data.get("hook", ""))
        data["slide_headlines"] = [_strip(h) for h in data.get("slide_headlines", [])]
        data["caption"] = _strip(data.get("caption", ""))[:200]
        data["hashtags"] = [_strip(h) for h in data.get("hashtags", [])]

        # Guarantee #ClearerThinking is first
        tags = data["hashtags"]
        ct = "#ClearerThinking"
        tags = [t for t in tags if t.lower() != ct.lower()]
        data["hashtags"] = [ct] + tags[:9]

        # Pad/trim headlines to match takeaway count
        n = len(takeaways)
        while len(data["slide_headlines"]) < n:
            data["slide_headlines"].append(_fallback(title, takeaways)["slide_headlines"][len(data["slide_headlines"])])
        data["slide_headlines"] = data["slide_headlines"][:n]

        return data

    except Exception:
        return _fallback(title, takeaways)
