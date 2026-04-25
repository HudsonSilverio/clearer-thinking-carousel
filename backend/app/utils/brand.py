"""
Clearer Thinking brand tokens.
Single source of truth for all image-generation and API responses.
"""

# ---------------------------------------------------------------------------
# Legacy top-level constants (kept for backwards compatibility)
# ---------------------------------------------------------------------------

BRAND_PRIMARY  = "#E8712A"
BRAND_ACCENT   = "#2B5EA7"
BRAND_DARK_BG  = "#1A1A2E"

SLIDE_WIDTH    = 1080
SLIDE_HEIGHT   = 1080

IG_HANDLE      = "@clearerthinking"

# ---------------------------------------------------------------------------
# New design constants (Instagram-accurate style)
# ---------------------------------------------------------------------------

SLIDE_BG            = "#E8EDF4"   # pale blue-gray — ALL content slides
COVER_BG            = "#F5F5F8"   # near-white — bottom area of cover slide
TEXT_HEADLINE       = "#555555"   # dark gray — headlines on content slides
TEXT_BODY           = "#6B6B6B"   # mid gray — body text on content slides
PROGRESS_BAR_COLOR  = "#E8A838"   # warm amber — progress bar on all non-cover slides
ACCENT_BLUE         = "#4A90D9"   # blue — CTA decorative elements only


# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------

class Colors:
    # Brand (legacy)
    PRIMARY       = BRAND_PRIMARY
    ACCENT        = BRAND_ACCENT
    DARK_BG       = BRAND_DARK_BG

    # New palette
    SLIDE_BG      = SLIDE_BG
    COVER_BG      = COVER_BG
    HEADLINE      = TEXT_HEADLINE
    BODY          = TEXT_BODY
    PROGRESS      = PROGRESS_BAR_COLOR
    CTA_BLUE      = ACCENT_BLUE

    # Utility
    WHITE         = "#FFFFFF"
    OFF_WHITE     = "#F7F7F7"
    BORDER        = "#E0E0E0"


# ---------------------------------------------------------------------------
# Typography
# ---------------------------------------------------------------------------

class Fonts:
    # Web names used in HTML/CSS
    HEADLINE_WEB  = "'Source Serif 4', serif"
    BODY_WEB      = "'Plus Jakarta Sans', sans-serif"

    # Legacy TTF paths (kept for any Pillow-based rendering)
    HEADING_FILE   = "assets/fonts/PlusJakartaSans-ExtraBold.ttf"
    BODY_FILE      = "assets/fonts/DMSans-Regular.ttf"
    BODY_BOLD_FILE = "assets/fonts/DMSans-Bold.ttf"
    FALLBACK       = "arial.ttf"


class FontSizes:
    COVER_TITLE   = 42
    SLIDE_HEADLINE = 42
    SLIDE_BODY    = 28
    CTA_HEADING   = 30
    CTA_URL       = 20


# ---------------------------------------------------------------------------
# Slide dimensions
# ---------------------------------------------------------------------------

class SlideDimensions:
    SQUARE_W   = 1080
    SQUARE_H   = 1080
    PORTRAIT_W = 1080
    PORTRAIT_H = 1350
    PADDING    = 65


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

class Layout:
    CORNER_RADIUS    = 24
    ELEMENT_GAP      = 40
    PROGRESS_BAR_H   = 8
    COVER_IMAGE_PCT  = 65    # % of slide height used by cover image
    ACCENT_BAR_W     = 40
    ACCENT_BAR_H     = 4


# ---------------------------------------------------------------------------
# Convenience bundle
# ---------------------------------------------------------------------------

BRAND = {
    "colors": Colors,
    "fonts": Fonts,
    "font_sizes": FontSizes,
    "slide": SlideDimensions,
    "layout": Layout,
    "site_name": "Clearer Thinking",
    "site_url": "clearerthinking.org",
    "tagline": "Make better decisions",
}
