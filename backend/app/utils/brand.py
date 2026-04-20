"""
Clearer Thinking brand tokens.
Single source of truth for all image-generation and API responses.
"""

# ---------------------------------------------------------------------------
# Top-level constants (checked by tests and other services)
# ---------------------------------------------------------------------------

BRAND_PRIMARY  = "#E8712A"   # orange — CTAs, highlights, accent lines
BRAND_ACCENT   = "#2B5EA7"   # blue  — links, secondary actions
BRAND_DARK_BG  = "#1A1A2E"   # dark navy — dark-mode slides, footers

SLIDE_WIDTH    = 1080
SLIDE_HEIGHT   = 1080

IG_HANDLE      = "@clearerthinking"

# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------

class Colors:
    # Brand
    PRIMARY       = BRAND_PRIMARY
    ACCENT        = BRAND_ACCENT
    DARK_BG       = BRAND_DARK_BG

    # Text
    HEADING       = "#303030"
    BODY          = "#737373"
    SUBTLE        = "#646464"
    WHITE         = "#FFFFFF"

    # Backgrounds
    OFF_WHITE     = "#F7F7F7"
    CREAM         = "#EBE5D6"

    # Utility
    BORDER        = "#E0E0E0"
    DISABLED      = "#C7C7C7"


# ---------------------------------------------------------------------------
# Typography
# ---------------------------------------------------------------------------

class Fonts:
    # Carousel brand fonts (TTF files in assets/fonts/)
    HEADING_FILE   = "assets/fonts/PlusJakartaSans-ExtraBold.ttf"   # Plus Jakarta Sans
    BODY_FILE      = "assets/fonts/DMSans-Regular.ttf"               # DM Sans
    BODY_BOLD_FILE = "assets/fonts/DMSans-Bold.ttf"

    # CSS / web names
    HEADING_WEB    = "Plus Jakarta Sans, sans-serif"
    BODY_WEB       = "DM Sans, sans-serif"

    # System fallback when font files are missing
    FALLBACK       = "arial.ttf"


class FontSizes:
    # Slide title (maps to site H1)
    SLIDE_TITLE   = 52
    # Slide subtitle / section heading (maps to H2)
    SLIDE_H2      = 36
    # Takeaway heading (maps to H3)
    TAKEAWAY_HEAD = 28
    # Body copy on slides
    SLIDE_BODY    = 22
    # Caption / metadata
    CAPTION       = 16
    # Branding tag on each slide
    BRAND_TAG     = 14


# ---------------------------------------------------------------------------
# Slide dimensions
# ---------------------------------------------------------------------------

class SlideDimensions:
    # Instagram / LinkedIn square carousel
    SQUARE_W      = 1080
    SQUARE_H      = 1080

    # Instagram portrait (4:5) — maximum feed real-estate
    PORTRAIT_W    = 1080
    PORTRAIT_H    = 1350

    # Safe inner padding (keeps text away from edges)
    PADDING       = 80


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

class Layout:
    # Rounded corner radius for cards and slides
    CORNER_RADIUS = 24

    # Vertical gap between elements inside a slide
    ELEMENT_GAP   = 32

    # Thickness of the accent underline beneath titles
    ACCENT_LINE_H = 6

    # Logo / brand strip height at the bottom of each slide
    BRAND_STRIP_H = 72


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
