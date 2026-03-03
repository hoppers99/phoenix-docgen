"""
Shared CSS styles for phoenix-docgen document generation.
Single source of truth for typography, tables, layout, and print styles.

All functions that use branded colours or fonts accept an optional `theme`
parameter (a Theme instance from theme.py).  When theme is None, built-in
defaults are used to preserve backward compatibility.
"""

import base64
from pathlib import Path

TEMPLATE_DIR = Path(__file__).parent / "templates"
FONT_DIR = TEMPLATE_DIR / "fonts"


def load_font_base64(font_path):
    """Load a font file as base64 string."""
    with open(font_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


def get_font_face_css(theme=None):
    """Generate @font-face CSS for the document font family."""
    if not theme:
        # No theme — use system fonts, no @font-face needed
        return ""

    family = theme.font_family()
    weights = theme.font_weights()
    if not weights:
        return ""

    rules = []
    for weight, path in sorted(weights.items()):
        b64 = load_font_base64(path)
        rules.append(f"""@font-face {{
            font-family: '{family}';
            src: url("data:font/truetype;base64,{b64}") format('truetype');
            font-weight: {weight};
            font-style: normal;
        }}""")
    return '\n        '.join(rules)


def get_page_css(doc_title="", classification="RESTRICTED", theme=None):
    """CSS @page rules for print/PDF output.

    Layout: cover (no margins, no footer), blank verso (with footer and
    'intentionally blank' text), then content pages with alternating
    left/right page numbers, centred document title, and classification
    marker on the opposite corner from the page number.
    """
    font_stack = theme.font_stack() if theme else "Arial, Helvetica, sans-serif"

    # Normalise: strip brackets if present, uppercase
    classification = classification.strip("[]").upper()
    cls_display = f"[{classification}]"

    return f"""
        @page {{
            size: A4;
            margin: 20mm 20mm 25mm 20mm;

            @bottom-center {{
                content: "{doc_title}";
                font-family: {font_stack};
                font-size: 10pt;
                color: #999999;
            }}
        }}

        @page:left {{
            @bottom-left {{
                content: counter(page);
                font-family: {font_stack};
                font-size: 10pt;
                color: #666666;
            }}
            @bottom-right {{
                content: "{cls_display}";
                font-family: {font_stack};
                font-size: 10pt;
                font-weight: 600;
                color: #999999;
                letter-spacing: 1pt;
            }}
        }}

        @page:right {{
            @bottom-left {{
                content: "{cls_display}";
                font-family: {font_stack};
                font-size: 10pt;
                font-weight: 600;
                color: #999999;
                letter-spacing: 1pt;
            }}
            @bottom-right {{
                content: counter(page);
                font-family: {font_stack};
                font-size: 10pt;
                color: #666666;
            }}
        }}

        @page:first {{
            margin: 0;
            @bottom-left {{ content: none; }}
            @bottom-right {{ content: none; }}
            @bottom-center {{ content: none; }}
        }}

        @page cover {{
            margin: 0;
            @bottom-left {{ content: none; }}
            @bottom-right {{ content: none; }}
            @bottom-center {{ content: none; }}
        }}

        @page blank {{
            @bottom-left {{ content: none; }}
            @bottom-right {{
                content: "{cls_display}";
                font-family: {font_stack};
                font-size: 10pt;
                font-weight: 600;
                color: #999999;
                letter-spacing: 1pt;
            }}
            @bottom-center {{
                content: "{doc_title}";
                font-family: {font_stack};
                font-size: 10pt;
                color: #999999;
            }}
        }}

        @page landscape {{
            size: A4 landscape;
            margin: 15mm 15mm 20mm 15mm;

            @bottom-center {{
                content: "{doc_title}";
                font-family: {font_stack};
                font-size: 10pt;
                color: #999999;
            }}
        }}

        @page landscape:left {{
            @bottom-left {{
                content: counter(page);
                font-family: {font_stack};
                font-size: 10pt;
                color: #666666;
            }}
            @bottom-right {{
                content: "{cls_display}";
                font-family: {font_stack};
                font-size: 10pt;
                font-weight: 600;
                color: #999999;
                letter-spacing: 1pt;
            }}
        }}

        @page landscape:right {{
            @bottom-left {{
                content: "{cls_display}";
                font-family: {font_stack};
                font-size: 10pt;
                font-weight: 600;
                color: #999999;
                letter-spacing: 1pt;
            }}
            @bottom-right {{
                content: counter(page);
                font-family: {font_stack};
                font-size: 10pt;
                color: #666666;
            }}
        }}
    """


def get_print_css():
    """CSS @media print rules."""
    return """
        @media print {
            html {
                background: white;
            }
            body {
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
                background: white;
            }
            .cover-page {
                margin: 0;
            }
            h2, h3, h4 {
                page-break-after: avoid;
            }
            table {
                page-break-inside: auto;
            }
            tr {
                page-break-inside: avoid;
            }
            p, li {
                orphans: 3;
                widows: 3;
            }
            pre {
                page-break-inside: avoid;
            }
        }
    """


def get_cover_css():
    """CSS for the SVG-based cover page."""
    return """
        .cover-page {
            page: cover;
            margin: 0;
            padding: 0;
        }

        .cover-page svg {
            display: block;
            width: 210mm;
            height: 297mm;
        }
    """


def get_content_css():
    """CSS for content wrapper and general content layout.

    In PDF: @page margins provide 20mm L/R spacing, content fills the area.
    In browser: max-width keeps it readable, centered on page.
    """
    return """
        .content-wrapper {
            background: white;
            margin: 0 auto;
            padding: 5mm 0;
        }

        @media screen {
            .content-wrapper {
                max-width: 210mm;
            }
        }

        .blank-verso {
            page: blank;
            page-break-before: always;
            page-break-after: always;
            text-align: center;
            padding-top: 120mm;
        }

        .blank-verso p {
            font-size: 10pt;
            color: #999999;
            font-style: italic;
            text-align: center;
        }

        .landscape-section {
            page: landscape;
            page-break-before: always;
            max-width: none;
        }

        .landscape-section table {
            table-layout: fixed;
            width: 100%;
            word-wrap: break-word;
        }

        /* Override pandoc's equal-width colgroup inline styles */
        .landscape-section table col {
            width: auto !important;
        }

        /* Appendix A — 8-column risk summary */
        .landscape-section table:first-of-type col:nth-child(1) { width: 7% !important; }
        .landscape-section table:first-of-type col:nth-child(3) { width: 3% !important; }
        .landscape-section table:first-of-type col:nth-child(4) { width: 3% !important; }
        .landscape-section table:first-of-type col:nth-child(5) { width: 9% !important; }
        .landscape-section table:first-of-type col:nth-child(6) { width: 9% !important; }
        .landscape-section table:first-of-type col:nth-child(7) { width: 9% !important; }

        /* Appendix B — 5-column tracker */
        .landscape-section table:nth-of-type(2) col:nth-child(1) { width: 4% !important; }
        .landscape-section table:nth-of-type(2) col:nth-child(3) { width: 8% !important; }
        .landscape-section table:nth-of-type(2) col:nth-child(4) { width: 12% !important; }
    """


def get_typography_css(theme=None):
    """CSS for headings, paragraphs, lists, links."""
    font_stack = theme.font_stack() if theme else "Arial, Helvetica, sans-serif"
    primary = theme.colour("primary") if theme else "#2c3e50"
    secondary = theme.colour("secondary") if theme else "#34495e"
    accent = theme.colour("accent") if theme else "#2980b9"

    return f"""
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}

        html {{
            background: white;
        }}

        @media screen {{
            html {{
                background: #f0f0f0;
            }}
        }}

        body {{
            font-family: {font_stack};
            font-size: 11pt;
            line-height: 1.5;
            color: #333333;
            background: white;
        }}

        h1 {{
            font-size: 20pt;
            font-weight: 500;
            color: {primary};
            margin-top: 18pt;
            margin-bottom: 4pt;
            page-break-after: avoid;
        }}

        h2 {{
            font-size: 16pt;
            font-weight: 500;
            color: {primary};
            margin-top: 16pt;
            margin-bottom: 4pt;
            padding-bottom: 2pt;
            border-bottom: 1px solid #E2E8F0;
            page-break-after: avoid;
        }}

        h3 {{
            font-size: 14pt;
            font-weight: 500;
            color: {secondary};
            margin-top: 8pt;
            margin-bottom: 4pt;
        }}

        h4 {{
            font-size: 12pt;
            font-weight: 500;
            color: {secondary};
            margin-top: 6pt;
            margin-bottom: 3pt;
        }}

        p {{
            margin-top: 0;
            margin-bottom: 6pt;
            text-align: justify;
        }}

        ul, ol {{
            margin-top: 0;
            margin-left: 18pt;
            margin-bottom: 6pt;
            padding-left: 0;
        }}

        li {{
            margin-bottom: 3pt;
        }}

        li > ul, li > ol {{
            margin-top: 3pt;
        }}

        strong {{
            font-weight: 600;
        }}

        hr {{
            border: none;
            border-top: 1px solid #E2E8F0;
            margin: 16pt 0;
        }}

        a {{
            color: #1E6E73;
            text-decoration: none;
        }}

        blockquote {{
            border-left: 4pt solid {accent};
            background: #f8fafc;
            margin: 8pt 0;
            padding: 8pt 12pt;
            font-size: 10pt;
            color: #666666;
        }}
    """


def get_table_css(theme=None):
    """CSS for tables."""
    secondary = theme.colour("secondary") if theme else "#34495e"

    return f"""
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 12pt 0;
            font-size: 10pt;
        }}

        th {{
            background-color: {secondary};
            color: white;
            font-weight: 600;
            text-align: left;
            padding: 6pt 8pt;
            border: 0.5pt solid {secondary};
        }}

        td {{
            padding: 5pt 8pt;
            border: 0.5pt solid #cccccc;
            vertical-align: top;
        }}

        tr:nth-child(even) td {{
            background-color: #f5f5f5;
        }}
    """


def get_code_css():
    """CSS for code blocks and inline code."""
    return """
        pre {
            font-family: 'SF Mono', 'Menlo', 'Monaco', 'Consolas', monospace;
            font-size: 8.5pt;
            line-height: 1.35;
            background-color: #f5f5f5;
            border: 1px solid #E2E8F0;
            border-radius: 4pt;
            padding: 12pt 16pt;
            overflow-x: auto;
            white-space: pre;
            margin: 8pt 0;
        }

        code {
            font-family: 'SF Mono', 'Menlo', 'Monaco', 'Consolas', monospace;
            font-size: 9pt;
            background-color: #f5f5f5;
            padding: 1pt 4pt;
            border-radius: 2pt;
        }

        pre code {
            background: none;
            padding: 0;
        }
    """


def get_diagram_css():
    """CSS for diagram containers, inline SVGs, and notes."""
    return """
        .diagram-container {
            margin: 16pt 0;
            page-break-inside: avoid;
        }

        .diagram-notes {
            background: #f8fafc;
            border: 1px solid #E2E8F0;
            border-radius: 4pt;
            padding: 10pt 16pt;
            margin: 12pt 0;
            font-size: 9.5pt;
        }

        svg {
            margin: 12pt 0;
            page-break-inside: avoid;
        }
    """


def get_reference_css():
    """CSS for superscript citations and section reference lists."""
    return """
        sup {
            font-size: 0.65em;
            line-height: 0;
            vertical-align: super;
            color: #666666;
        }

        .section-references {
            font-size: 8pt;
            color: #888888;
            margin-top: 12pt;
        }

        .section-references p {
            font-size: 8pt;
            margin-bottom: 1pt;
            text-align: left;
            line-height: 1.3;
        }
    """


def get_footnote_css(theme=None):
    """CSS for Pandoc-generated footnotes.

    Pandoc wraps footnotes in <section class="footnotes"> with an <ol> inside.
    Each footnote gets a backlink (↩︎). In-text references are <sup> with
    <a class="footnote-ref">.
    """
    primary = theme.colour("primary") if theme else "#2c3e50"

    return f"""
        /* --- Footnote references (in-text superscripts) --- */
        a.footnote-ref {{
            color: {primary};
            text-decoration: none;
            font-weight: 500;
        }}

        /* --- Footnote section (end of document/chapter) --- */
        section.footnotes {{
            margin-top: 24pt;
            padding-top: 10pt;
            border-top: 1px solid #E2E8F0;
            font-size: 9pt;
            color: #555555;
            line-height: 1.4;
        }}

        section.footnotes hr {{
            display: none;
        }}

        section.footnotes ol {{
            margin-left: 14pt;
            padding-left: 0;
        }}

        section.footnotes li {{
            margin-bottom: 4pt;
        }}

        section.footnotes li p {{
            font-size: 9pt;
            margin-bottom: 2pt;
            text-align: left;
        }}

        /* --- Backlink arrow --- */
        section.footnotes a.footnote-back {{
            color: #999999;
            text-decoration: none;
            font-size: 8pt;
            margin-left: 3pt;
        }}

        /* --- Compacted footnotes (duplicate text merged) --- */
        ol.compact-footnotes {{
            list-style: none;
            margin-left: 0;
            padding-left: 0;
        }}

        ol.compact-footnotes li.compact-fn {{
            margin-bottom: 4pt;
        }}

        .fn-nums {{
            color: {primary};
            font-weight: 600;
            font-size: 9pt;
        }}
    """


def get_footer_css(theme=None):
    """CSS for document footer."""
    secondary = theme.colour("secondary") if theme else "#34495e"

    return f"""
        .doc-footer {{
            margin-top: 36pt;
            padding-top: 12pt;
            border-top: 2pt solid {secondary};
            text-align: center;
            font-size: 8pt;
            color: #666666;
        }}

        .doc-footer p {{
            margin: 3pt 0;
            text-align: center;
        }}
    """


def _svg_data_uri(svg):
    """Encode an SVG string as a CSS data URI."""
    import urllib.parse
    return 'url("data:image/svg+xml,' + urllib.parse.quote(svg.strip(), safe='/:@!$&\'()*+,;=') + '")'


def get_alert_css(theme=None):
    """CSS for GitHub-style alert boxes and inline alert glyphs.

    Icons are inline SVGs matching the Typora/GitHub style:
    circle-i (note), lightbulb (tip), circle-! (important),
    triangle-! (warning), octagon-! (caution).

    Only the [!NOTE] type uses the theme primary colour; the rest use
    fixed semantic colours that are consistent across themes.
    """
    note_colour = theme.colour("primary") if theme else "#2c3e50"

    # ── SVG icon definitions ───────────────────────────────────────
    # Each is 16x16, stroke-based, matching Typora's outline style.
    svgs = {
        'note': {
            'colour': note_colour,
            # Circle with "i" — information
            'svg': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><circle cx="8" cy="8" r="7" fill="none" stroke="{c}" stroke-width="1.5"/><line x1="8" y1="7" x2="8" y2="11.5" stroke="{c}" stroke-width="1.8" stroke-linecap="round"/><circle cx="8" cy="4.5" r="1" fill="{c}"/></svg>',
        },
        'tip': {
            'colour': '#1a7f37',
            # Lightbulb outline
            'svg': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path d="M8 1.5a4.5 4.5 0 0 0-2.8 8c.5.4.8 1 .8 1.6V12h4v-.9c0-.6.3-1.2.8-1.6A4.5 4.5 0 0 0 8 1.5z" fill="none" stroke="{c}" stroke-width="1.3" stroke-linejoin="round"/><line x1="6" y1="14" x2="10" y2="14" stroke="{c}" stroke-width="1.3" stroke-linecap="round"/><line x1="6" y1="12" x2="10" y2="12" stroke="{c}" stroke-width="1" stroke-linecap="round"/></svg>',
        },
        'important': {
            'colour': '#7d3c98',
            # Circle with "!" — exclamation
            'svg': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><circle cx="8" cy="8" r="7" fill="none" stroke="{c}" stroke-width="1.5"/><line x1="8" y1="4" x2="8" y2="9" stroke="{c}" stroke-width="1.8" stroke-linecap="round"/><circle cx="8" cy="11.5" r="1" fill="{c}"/></svg>',
        },
        'warning': {
            'colour': '#bf8700',
            # Triangle with "!" — warning
            'svg': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path d="M7.13 2.24a1 1 0 0 1 1.74 0l5.5 9.6A1 1 0 0 1 13.5 13.5h-11a1 1 0 0 1-.87-1.66z" fill="none" stroke="{c}" stroke-width="1.3" stroke-linejoin="round"/><line x1="8" y1="6" x2="8" y2="9.5" stroke="{c}" stroke-width="1.6" stroke-linecap="round"/><circle cx="8" cy="11.5" r="0.9" fill="{c}"/></svg>',
        },
        'caution': {
            'colour': '#cf222e',
            # Octagon with "!" — stop/caution
            'svg': '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 16 16"><path d="M5.3 1.5h5.4L15 5.3v5.4l-4.3 4.3H5.3L1 10.7V5.3z" fill="none" stroke="{c}" stroke-width="1.3" stroke-linejoin="round"/><line x1="8" y1="4.5" x2="8" y2="9" stroke="{c}" stroke-width="1.6" stroke-linecap="round"/><circle cx="8" cy="11.2" r="0.9" fill="{c}"/></svg>',
        },
    }

    # Build CSS with SVG data URIs
    icon_rules = []
    glyph_rules = []
    for name, info in svgs.items():
        c = info['colour']
        svg_str = info['svg'].replace('{c}', c)
        uri = _svg_data_uri(svg_str)

        # Block alert icon (in title bar)
        icon_rules.append(f"""
        .alert-{name} .alert-icon {{
            background-image: {uri};
        }}""")

        # Inline glyph
        glyph_rules.append(f"""
        .alert-glyph-{name} {{
            background-image: {uri};
        }}""")

    icons_css = '\n'.join(icon_rules)
    glyphs_css = '\n'.join(glyph_rules)

    return f"""
        /* ── Block-level alerts ─────────────────────────────────── */
        .alert {{
            border-left: 4pt solid #888888;
            background: #f8fafc;
            margin: 10pt 0;
            padding: 8pt 12pt;
            font-size: 10pt;
            border-radius: 0 3pt 3pt 0;
        }}

        .alert p {{
            margin: 4pt 0;
        }}

        .alert-title {{
            font-weight: 700;
            font-size: 10pt;
            margin-bottom: 4pt !important;
        }}

        .alert-icon {{
            display: inline-block;
            width: 12pt;
            height: 12pt;
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
            vertical-align: -1.5pt;
            margin-right: 3pt;
        }}

        /* Type colours — border + title */
        .alert-note            {{ border-left-color: {note_colour}; }}
        .alert-note .alert-title {{ color: {note_colour}; }}

        .alert-tip             {{ border-left-color: #1a7f37; }}
        .alert-tip .alert-title  {{ color: #1a7f37; }}

        .alert-important       {{ border-left-color: #7d3c98; }}
        .alert-important .alert-title {{ color: #7d3c98; }}

        .alert-warning         {{ border-left-color: #bf8700; }}
        .alert-warning .alert-title {{ color: #bf8700; }}

        .alert-caution         {{ border-left-color: #cf222e; }}
        .alert-caution .alert-title {{ color: #cf222e; }}

        {icons_css}

        /* ── Inline alert glyphs ────────────────────────────────── */
        .alert-glyph {{
            display: inline-block;
            width: 11pt;
            height: 11pt;
            background-size: contain;
            background-repeat: no-repeat;
            background-position: center;
            vertical-align: -1.5pt;
            margin: 0 2pt;
        }}

        {glyphs_css}
    """


def get_full_css(include_toc=False, include_chapter_dividers=False,
                 include_info_block=False, include_appendix_dividers=False,
                 doc_title="", classification="RESTRICTED", theme=None):
    """Build the complete CSS string from all components.

    Args:
        include_toc: Include nav#TOC styles (for individual docs with pandoc TOC)
        include_chapter_dividers: Include chapter divider styles (for combined doc)
        include_info_block: Include info-block styles (for individual docs)
        include_appendix_dividers: Include appendix divider styles (for combined v2)
        doc_title: Document title for the centred page footer
        classification: Classification marker for page footers (e.g. RESTRICTED, INTERNAL)
        theme: Optional Theme instance for branded colours/fonts
    """
    font_faces = get_font_face_css(theme=theme)
    sections = [
        font_faces,
        get_page_css(doc_title=doc_title, classification=classification, theme=theme),
        get_print_css(),
        get_typography_css(theme=theme),
        get_cover_css(),
        get_content_css(),
    ]

    if include_info_block:
        sections.append(get_info_block_css())

    if include_chapter_dividers:
        sections.append(get_chapter_divider_css(theme=theme))

    if include_appendix_dividers:
        sections.append(get_appendix_divider_css(theme=theme))

    if include_toc:
        sections.append(get_toc_css(theme=theme))

    sections.extend([
        get_table_css(theme=theme),
        get_code_css(),
        get_diagram_css(),
        get_reference_css(),
        get_footnote_css(theme=theme),
        get_alert_css(theme=theme),
        get_footer_css(theme=theme),
    ])

    return '\n'.join(sections)


def get_toc_css(theme=None):
    """CSS for pandoc-generated table of contents."""
    primary = theme.colour("primary") if theme else "#2c3e50"

    return f"""
        nav#TOC {{
            background: #f8fafc;
            border: 1px solid #E2E8F0;
            border-radius: 4pt;
            padding: 12pt 18pt;
            margin: 16pt 0 24pt 0;
        }}

        nav#TOC > ul {{
            list-style: none;
            padding-left: 0;
        }}

        nav#TOC li {{
            margin-bottom: 4pt;
        }}

        nav#TOC a {{
            color: {primary};
            font-weight: 500;
        }}
    """


def get_info_block_css():
    """CSS for document info block (individual docs)."""
    return """
        .info-block {
            margin-bottom: 24pt;
        }

        .info-block .doc-title {
            font-size: 24pt;
            font-weight: 600;
            color: #333333;
            margin: 0 0 4pt 0;
        }

        .info-block .doc-subtitle {
            font-size: 14pt;
            font-weight: 400;
            color: #666666;
            margin: 0 0 16pt 0;
            letter-spacing: 1pt;
        }

        .info-block .doc-meta {
            margin-bottom: 16pt;
        }

        .info-block .doc-meta p {
            margin: 0 0 2pt 0;
            font-size: 10pt;
            text-align: left;
        }

        .info-block .divider {
            border: none;
            border-top: 1pt solid #333333;
            margin: 16pt 0 24pt 0;
        }
    """


def get_chapter_divider_css(theme=None):
    """CSS for chapter dividers (combined doc)."""
    secondary = theme.colour("secondary") if theme else "#34495e"

    return f"""
        .chapter-divider {{
            background: {secondary};
            padding: 20mm 20mm;
            margin: 0;
            color: white;
            page-break-before: always;
        }}

        .chapter-divider h1 {{
            font-size: 28pt;
            font-weight: 600;
            color: white;
            margin: 0 0 8pt 0;
            border: none;
        }}

        .chapter-divider .chapter-subtitle {{
            font-size: 12pt;
            font-weight: 400;
            color: rgba(255,255,255,0.7);
            margin: 0 0 16pt 0;
        }}

        .chapter-divider .chapter-meta {{
            font-size: 10pt;
            color: rgba(255,255,255,0.6);
        }}
    """


def get_appendix_divider_css(theme=None):
    """CSS for appendix dividers (combined v2 doc)."""
    secondary = theme.colour("secondary") if theme else "#34495e"
    primary = theme.colour("primary") if theme else "#2c3e50"

    return f"""
        .appendix-divider {{
            background: {secondary};
            padding: 20mm 20mm;
            margin: 0;
            color: white;
            page-break-before: always;
        }}

        .appendix-divider h1 {{
            font-size: 28pt;
            font-weight: 600;
            color: white;
            margin: 0 0 8pt 0;
            border: none;
        }}

        .appendix-divider .chapter-subtitle {{
            font-size: 12pt;
            font-weight: 400;
            color: rgba(255,255,255,0.7);
            margin: 0;
        }}

        .appendix-body h3 {{
            color: {primary};
            margin-top: 16pt;
        }}
    """
