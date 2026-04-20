"""
Clearer Thinking brand tokens extracted from clearerthinking.org.
Single source of truth for all image-generation and API responses.
"""

# ---------------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------------

class Colors:
    # Text
    HEADING       = "#303030"   # rgb(48,48,48)  — h1/h2/h3
    BODY          = "#737373"   # rgb(115,115,115) — article paragraphs
    SUBTLE        = "#646464"   # rgb(100,100,100) — secondary text
    NAV           = "#333333"   # rgb(51,51,51)   — nav / header text

    # Backgrounds
    WHITE         = "#FFFFFF"
    OFF_WHITE     = "#F7F7F7"   # secondary page background
    CREAM         = "#EBE5D6"   # warm accent background
    DARK          = "#303030"   # dark card / inverted slide

    # Brand accent
    BLUE          = "#0885F8"   # rgb(8,133,248)  — primary CTA / highlight
    BLUE_LINK     = "#337AB7"   # rgb(51,122,183) — inline links
    CYAN          = "#00A6ED"   # rgb(0,166,237)  — secondary accent

    # Utility
    BORDER        = "#E0E0E0"
    DISABLED      = "#C7C7C7"   # rgb(199,199,199)


# ---------------------------------------------------------------------------
# Typography
# ---------------------------------------------------------------------------

class Fonts:
    # Web-font names as served by Wix (for reference / CSS use)
    HEADING_WEB   = "avenir-lt-w01_85-heavy1475544, sans-serif"
    BODY_WEB      = "roboto-bold, roboto, sans-serif"

    # Google Fonts equivalents used for Pillow image rendering
    # (download to assets/fonts/ via setup script)
    HEADING_FILE  = "assets/fonts/Nunito-ExtraBold.ttf"   # closest Avenir Heavy match
    BODY_FILE     = "assets/fonts/Roboto-Regular.ttf"
    BODY_BOLD_FILE= "assets/fonts/Roboto-Bold.ttf"

    # System fallback when font files are missing
    FALLBACK      = "arial.ttf"


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
