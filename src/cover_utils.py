"""
Cover page utilities — single source of truth for cover page generation.
Uses an SVG template with placeholder substitution.

When a Theme is provided, paths and colours are resolved from the theme.
Otherwise falls back to built-in template paths for backward compatibility.
"""

import base64
from pathlib import Path

TEMPLATE_DIR = Path(__file__).parent / "templates"
SVG_TEMPLATE_PATH = TEMPLATE_DIR / "cover-page-template-a4.svg"
LOGO_PATH = TEMPLATE_DIR / "logo.png"


def _get_logo_base64(logo_path):
    """Load a logo file as a base64 data URI string."""
    logo_path = Path(logo_path)
    if logo_path.exists():
        with open(logo_path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    return ""


def fill_cover_svg(
    title_line1: str,
    title_line2: str,
    subtitle: str,
    author: str,
    year: str,
    classification: str,
    version: str = "",
    theme=None,
) -> str:
    """Load the SVG template and fill in placeholders.

    Returns the filled SVG string with the logo embedded.
    """
    # Resolve template path
    if theme:
        template_path = theme.cover_template_path()
    else:
        template_path = SVG_TEMPLATE_PATH

    svg = template_path.read_text(encoding="utf-8")

    # Fill placeholders
    svg = svg.replace("{{TITLE_LINE1}}", title_line1)
    svg = svg.replace("{{TITLE_LINE2}}", title_line2)
    svg = svg.replace("{{SUBTITLE}}", subtitle)
    svg = svg.replace("{{AUTHOR}}", author)
    svg = svg.replace("{{YEAR}}", year)
    svg = svg.replace("{{CLASSIFICATION}}", classification)
    svg = svg.replace("{{VERSION}}", version)

    # Fill organisation footer (theme-aware)
    if theme:
        org_footer = f"{theme.org('name')} | {theme.org('address')}"
    else:
        org_footer = ""
    svg = svg.replace("{{ORG_FOOTER}}", org_footer)

    # Resolve logo
    if theme:
        logo_path = theme.logo_path()
        pos = theme.logo_position()
    else:
        logo_path = LOGO_PATH
        pos = {"x": 85, "y": 75, "width": 108, "height": 108}

    logo_b64 = _get_logo_base64(logo_path)
    if logo_b64:
        logo_element = (
            f'<image x="{pos["x"]}" y="{pos["y"]}" '
            f'width="{pos["width"]}" height="{pos["height"]}"'
            f' href="data:image/png;base64,{logo_b64}"'
            f' preserveAspectRatio="xMidYMid meet" />'
        )
        # Insert before the closing </svg> tag
        svg = svg.replace("</svg>", f"  {logo_element}\n</svg>")

    return svg


def create_cover_html(
    title_line1: str,
    title_line2: str,
    subtitle: str,
    author: str,
    year: str,
    classification: str,
    version: str = "",
    theme=None,
) -> str:
    """Create a cover page HTML div using the SVG template.

    The SVG is embedded inline and scaled to fill the A4 cover page.
    """
    svg = fill_cover_svg(
        title_line1, title_line2, subtitle, author, year, classification,
        version=version, theme=theme,
    )

    # Strip XML declaration for clean inline embedding
    if svg.startswith("<?xml"):
        svg = svg[svg.index("?>") + 2:].strip()

    # WeasyPrint can't render complex SVG filters (feFlood/feGaussianBlur).
    # Remove the filter reference so the year badge rect renders cleanly.
    svg = svg.replace('filter:url(#filter27)', '')

    # CairoSVG incorrectly fills <g> bounding boxes when fill is set on
    # a group element. Remove g4's group fill (SVG spec says fill on <g>
    # only sets inherited fill for children, it shouldn't render geometry).
    svg = svg.replace(
        'style="fill:url(#linearGradient14)"',
        ''
    )

    # CairoSVG can't resolve gradient stops inherited via xlink:href.
    # Replace linearGradient15 (which inherits from linearGradient13) with
    # a self-contained gradient using objectBoundingBox to avoid transform
    # coordinate issues. Same visual: transparent left → accent right.
    accent = theme.colour("accent") if theme else "#2980b9"
    swish_gradient = (
        '<linearGradient id="swishGradient" '
        'gradientUnits="objectBoundingBox" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0.18" style="stop-color:#000000;stop-opacity:0;" />'
        f'<stop offset="1" style="stop-color:{accent};stop-opacity:1;" />'
        '</linearGradient>'
    )
    svg = svg.replace('</defs>', f'  {swish_gradient}\n  </defs>')
    svg = svg.replace(
        'style="fill:url(#linearGradient15)"',
        'style="fill:url(#swishGradient)"'
    )

    return f"""
    <div class="cover-page">
        {svg}
    </div>
    """
