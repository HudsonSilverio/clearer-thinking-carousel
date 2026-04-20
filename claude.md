# Clearer Thinking Carousel — Project Guide

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
- **Cover slide:** title + cover image from the blog post
- **Takeaway slides:** one key takeaway per slide, no emojis
- **CTA slide:** "Read the full article at clearerthinking.org"

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Server health check |
| POST | `/api/blog/scrape` | Scrape title, cover image, and takeaways from a CT blog URL |

### POST /api/blog/scrape
**Request body:**
```json
{ "url": "https://www.clearerthinking.org/post/..." }
```
**Response:**
```json
{
  "url": "...",
  "title": "Post Title",
  "cover_image": "https://...",
  "takeaways": ["Takeaway one", "Takeaway two"]
}
```

## Blog Scraping Rules

1. Only accept URLs from `clearerthinking.org/post/`
2. Extract the H1 as the post title
3. Skip the shared site banner image (`a8e1f3e15ccb41b88df85a10bb90531a`); use the first article-specific image
4. Key takeaways are the lines immediately after "Short of time? Read the key takeaways." that begin with an emoji
5. Strip all emojis from every extracted string before returning
6. Use Playwright (headless Chromium) — the site is Wix/JS-rendered and cannot be scraped with static HTTP
7. Return HTTP 422 if the page title is empty (invalid or non-existent post)

## Project Structure

```
clearer-thinking-carousel/
├── backend/
│   ├── app/
│   │   ├── api/routes/blog.py     # POST /api/blog/scrape
│   │   ├── services/scraper.py    # Playwright scraper
│   │   └── utils/brand.py        # Brand tokens
│   ├── tests/test_scraper.py
│   └── requirements.txt
├── dashboard/                     # Next.js 16 + Tailwind v4
│   └── src/app/
├── assets/
│   ├── fonts/                     # Plus Jakarta Sans, DM Sans TTF files
│   ├── templates/
│   └── brand/
└── docs/
```
