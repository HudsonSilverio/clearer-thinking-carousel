# Clearer Thinking Carousel — Project Guide

**Current Phase: 2**

## Phase Checklist
- [x] Phase 1: Scraper, FastAPI backend, Next.js dashboard scaffold
- [ ] Phase 2: AI content generation (Gemini) + carousel image builder

## Brand Guidelines

### Colors
- **Brand Primary:** `#E8712A` (orange — CTAs, highlights, accent lines)
- **Brand Accent:** `#2B5EA7` (blue — links, secondary actions)
- **Brand Dark Background:** `#1A1A2E` (dark navy — dark-mode slides, footers)
- **White:** `#FFFFFF`
- **Off-white:** `#F7F7F7`
- **Body text:** `#303030`
- **Subtle text:** `#737373`

### Typography
- **Heading font:** `Plus Jakarta Sans` (Extra Bold / Bold)
- **Body font:** `DM Sans` (Regular / Medium)
- All text on carousel slides must be free of emojis.

## Carousel Specifications

- **Format:** Square 1080×1080 px (Instagram / LinkedIn)
- **Portrait option:** 1080×1350 px (4:5)
- **Padding:** 80 px inner safe zone
- **Corner radius:** 24 px on cards
- **Slides per carousel:** typically 5–7 (1 cover + takeaways + CTA)
- **Brand strip:** 72 px footer strip on every slide with `@clearerthinking`
- **Cover slide:** title + cover image from the blog post, hook text, Instagram handle
- **Takeaway slides:** one key takeaway per slide, no emojis, alternating dark/accent backgrounds
- **CTA slide:** gradient orange-to-blue, "Read the full article", clearerthinking.org/blog
- **Progress bar:** bottom of every slide showing current position (e.g. "1/7")

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Server health check |
| POST | `/api/blog/scrape` | Scrape title, cover image, and takeaways from a CT blog URL |
| POST | `/api/carousel/generate` | Full pipeline: scrape → AI → build HTML → render PNGs + PDF |
| GET | `/api/carousel/{id}/slide/{index}` | Return a single slide PNG |
| GET | `/api/carousel/{id}/pdf` | Return the full carousel PDF |
| GET | `/api/carousel/{id}/info` | Return carousel metadata |

## Blog Scraping Rules

1. Only accept URLs from `clearerthinking.org/post/`
2. Extract the H1 as the post title
3. Skip the shared site banner image (`a8e1f3e15ccb41b88df85a10bb90531a`); use the first article-specific image
4. Key takeaways are the lines immediately after "Short of time? Read the key takeaways." that begin with an emoji
5. Fallback: detect first run of 3+ consecutive emoji-prefixed lines if marker is absent
6. Strip all emojis from every extracted string before returning
7. Use Playwright (headless Chromium) — the site is Wix/JS-rendered and cannot be scraped with static HTTP
8. Return HTTP 422 if the page title is empty (invalid or non-existent post)

## Project Structure

```
clearer-thinking-carousel/
├── backend/
│   ├── app/
│   │   ├── api/routes/
│   │   │   ├── blog.py          # POST /api/blog/scrape
│   │   │   └── carousel.py      # POST /api/carousel/generate + GET endpoints
│   │   ├── services/
│   │   │   ├── scraper.py       # Playwright blog scraper
│   │   │   ├── ai_generator.py  # Gemini 1.5 Flash — hook, headlines, caption, hashtags
│   │   │   ├── carousel_builder.py  # HTML slide builder (1080x1080)
│   │   │   └── image_renderer.py    # Playwright PNG renderer + Pillow PDF
│   │   └── utils/brand.py       # Brand tokens (colors, fonts, dimensions)
│   ├── tests/
│   │   ├── test_scraper.py
│   │   └── test_phase2.py
│   └── requirements.txt
├── dashboard/                   # Next.js 16 + Tailwind v4
│   └── src/app/
├── assets/
│   ├── fonts/                   # Plus Jakarta Sans, DM Sans TTF files
│   ├── templates/
│   └── brand/
├── generated_carousels/         # Output folder — gitignored
└── docs/
```

## AI Generator Contract (ai_generator.py)

Input: `title: str`, `takeaways: list[str]`
Output JSON:
```json
{
  "hook": "6-10 word compelling hook, no emojis",
  "slide_headlines": ["5-10 word headline per takeaway"],
  "caption": "Instagram caption under 200 chars, no emojis",
  "hashtags": ["#ClearerThinking", "...9 more"]
}
```
- Uses `GEMINI_API_KEY` from `.env`
- Falls back to basic content if API call fails
- Strips emojis from all output
