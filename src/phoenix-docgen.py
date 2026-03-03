#!/usr/bin/env python3
"""
phoenix-docgen — branded document builder.

Converts markdown documents to professionally styled HTML and PDF
using configurable themes (fonts, colours, cover, logo).

Usage:
    phoenix-docgen init document.md [--title1 TEXT] [--title2 TEXT] ...
    phoenix-docgen init --config project.yaml [--chapters FILE ...]
    phoenix-docgen build document.md [--pdf] [--version TEXT] ...
    phoenix-docgen combine --config project.yaml [--pdf]
    phoenix-docgen help [topic]
"""

import argparse
import datetime
import re
import subprocess
import sys
import textwrap
from pathlib import Path

import yaml

from cover_utils import create_cover_html
from help_topics import show_help
from shared_styles import get_full_css
from theme import load_config, resolve_theme, resolve_themes_dir

SCRIPT_DIR = Path(__file__).parent


# ── Helpers ───────────────────────────────────────────────────────────

def normalise_classification(value):
    """Normalise classification: strip brackets, uppercase, then re-wrap.

    Accepts any of: RESTRICTED, [RESTRICTED], "[RESTRICTED]", restricted
    Always returns: [RESTRICTED]
    """
    cleaned = str(value).strip().strip('"').strip("'").strip("[]").upper()
    return f"[{cleaned}]"


# ── Defaults ──────────────────────────────────────────────────────────

_BUILTIN_DEFAULTS = {
    "title_line1": "DOCUMENT",
    "title_line2": "TITLE",
    "subtitle": "",
    "version": "v0.1 DRAFT",
    "doc_type": "Report",
    "classification": "[RESTRICTED]",
    "author": "",
    "year": str(datetime.date.today().year),
    "toc": True,
    "toc_depth": 3,
    "info_block": True,
}

# Module-level mutable reference — updated by main() once theme is resolved
DEFAULTS = dict(_BUILTIN_DEFAULTS)


def get_defaults(theme=None):
    """Return defaults merged with theme doc_defaults if available."""
    defaults = dict(_BUILTIN_DEFAULTS)
    if theme:
        theme_defaults = theme.doc_defaults()
        for key in ("subtitle", "author", "classification"):
            if key in theme_defaults:
                defaults[key] = theme_defaults[key]
    return defaults


# ── YAML front-matter parsing ────────────────────────────────────────

def parse_front_matter(md_path):
    """Extract YAML front-matter and body from a markdown file.

    Returns (metadata_dict, body_text).  If no front-matter is found,
    metadata_dict is empty and body_text is the full file content.
    """
    text = md_path.read_text(encoding="utf-8")

    if not text.startswith("---"):
        return {}, text

    # Find closing ---
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text

    front_matter = text[3:end].strip()
    body = text[end + 4:].lstrip("\n")

    try:
        meta = yaml.safe_load(front_matter) or {}
    except yaml.YAMLError as e:
        print(f"  WARNING: Could not parse front-matter: {e}")
        meta = {}

    return meta, body


def merge_config(defaults, front_matter, cli_args):
    """Merge configuration from three sources (lowest → highest priority).

    CLI args override front-matter which overrides defaults.
    Only non-None CLI values are applied.
    """
    config = dict(defaults)
    config.update({k: v for k, v in front_matter.items() if v is not None})
    config.update({k: v for k, v in cli_args.items() if v is not None})
    return config


# ── Markdown → HTML conversion ───────────────────────────────────────

def convert_md_to_html(source_path, toc=True, toc_depth=3):
    """Convert a markdown file to HTML body using pandoc."""
    cmd = [
        "pandoc", str(source_path),
        "--to", "html5",
        "--no-highlight",
    ]
    if toc:
        cmd.extend(["--toc", f"--toc-depth={toc_depth}"])

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: pandoc failed for {source_path}: {result.stderr}")
        return None
    return result.stdout


def convert_body_to_html(body_text, toc=True, toc_depth=3):
    """Convert markdown body text (no front-matter) to HTML via pandoc stdin."""
    cmd = [
        "pandoc",
        "--from", "markdown",
        "--to", "html5",
        "--no-highlight",
    ]
    if toc:
        cmd.extend(["--toc", f"--toc-depth={toc_depth}"])

    result = subprocess.run(cmd, input=body_text, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: pandoc failed: {result.stderr}")
        return None
    return result.stdout


def process_alerts(html):
    """Convert GitHub-style alerts to styled HTML.

    Handles two forms:

    1. Block-level alerts (blockquote with [!TYPE] marker):
       > [!NOTE]
       > Content here
       Becomes a styled alert box with icon, coloured border, and title.

    2. Inline alert glyphs (bare [!TYPE] in running text):
       Some text [!WARNING] about something
       Becomes an inline glyph: a small coloured icon/label.

    Supported types: NOTE, TIP, IMPORTANT, WARNING, CAUTION
    """
    ALERT_TYPES = {
        'NOTE':      {'label': 'Note'},
        'TIP':       {'label': 'Tip'},
        'IMPORTANT': {'label': 'Important'},
        'WARNING':   {'label': 'Warning'},
        'CAUTION':   {'label': 'Caution'},
    }

    types_pattern = '|'.join(ALERT_TYPES.keys())

    # ── 1. Block-level alerts ──────────────────────────────────────────
    # Match <blockquote> whose first <p> starts with [!TYPE]
    # Pattern A: [!TYPE] on same line as content  → <p>[!NOTE] Content...</p>
    # Pattern B: [!TYPE] alone in its own <p>      → <p>[!NOTE]</p><p>Content</p>

    def replace_blockquote(m):
        bq_content = m.group(1)
        # Find the alert marker in the first <p>
        marker_match = re.match(
            r'\s*<p>\s*\[!(' + types_pattern + r')\]\s*(.*?)</p>',
            bq_content, re.DOTALL)
        if not marker_match:
            return m.group(0)  # not an alert blockquote, leave as-is

        alert_type = marker_match.group(1)
        remaining_inline = marker_match.group(2).strip()
        rest_of_bq = bq_content[marker_match.end():].strip()

        info = ALERT_TYPES[alert_type]

        # Build inner content
        if remaining_inline:
            inner = f'<p>{remaining_inline}</p>'
            if rest_of_bq:
                inner += '\n' + rest_of_bq
        else:
            inner = rest_of_bq if rest_of_bq else ''

        return (
            f'<div class="alert alert-{alert_type.lower()}">'
            f'<p class="alert-title">'
            f'<span class="alert-icon"></span> {info["label"]}'
            f'</p>'
            f'{inner}'
            f'</div>'
        )

    html = re.sub(
        r'<blockquote>\s*(.*?)\s*</blockquote>',
        replace_blockquote, html, flags=re.DOTALL)

    # ── 2. Inline alert glyphs ─────────────────────────────────────────
    # Replace bare [!TYPE] strings (not inside alert divs) with a glyph span.
    # Only match occurrences NOT at the very start of a <p> (those were handled
    # above as blockquote alerts — if any survived, they're not in blockquotes).
    for atype in ALERT_TYPES:
        glyph = (
            f'<span class="alert-glyph alert-glyph-{atype.lower()}">'
            f'</span>'
        )
        html = html.replace(f'[!{atype}]', glyph)

    return html


def compact_footnotes(html):
    """Compact duplicate footnotes into combined entries.

    When multiple footnotes have identical text (e.g. the same source cited
    several times), merge them into a single entry showing all numbers.
    For example, if footnotes 1, 4, and 7 all say "Salesforce codebase
    analysis", the footnote list shows:

        [1][4][7] Salesforce codebase analysis — ...

    In-text superscript references remain unchanged (each still links to
    its own number).  Backlinks from the merged entry point back to all
    original reference locations.
    """
    # Find the footnotes section
    section_match = re.search(
        r'(<section[^>]*class="[^"]*footnotes[^"]*"[^>]*>)\s*<hr\s*/?\s*>\s*<ol>(.*?)</ol>\s*</section>',
        html, re.DOTALL)
    if not section_match:
        return html

    section_open = section_match.group(1)
    ol_content = section_match.group(2)

    # Parse each <li> — extract id, text content, and backlink(s)
    li_pattern = re.compile(
        r'<li\s+id="(fn\d+)"[^>]*>\s*<p>(.*?)</p>\s*</li>',
        re.DOTALL)

    footnotes = []
    for m in li_pattern.finditer(ol_content):
        fn_id = m.group(1)
        inner = m.group(2).strip()

        # Separate text from backlink(s)
        backlinks = re.findall(
            r'<a\s+href="[^"]*"\s+class="footnote-back"[^>]*>.*?</a>',
            inner)
        text = re.sub(
            r'\s*<a\s+href="[^"]*"\s+class="footnote-back"[^>]*>.*?</a>',
            '', inner).strip()

        # Extract the number from the id (fn1 -> 1)
        num = re.search(r'\d+', fn_id).group()

        footnotes.append({
            'id': fn_id,
            'num': num,
            'text': text,
            'backlinks': backlinks,
        })

    if not footnotes:
        return html

    # Group by identical text content
    from collections import OrderedDict
    groups = OrderedDict()
    for fn in footnotes:
        if fn['text'] not in groups:
            groups[fn['text']] = []
        groups[fn['text']].append(fn)

    # Check if there are any duplicates worth compacting
    has_duplicates = any(len(fns) > 1 for fns in groups.values())
    if not has_duplicates:
        return html

    # Build compacted footnote list
    new_items = []
    for text, fns in groups.items():
        # Combined number label: [1][4][7]
        nums_label = ''.join(f'[{fn["num"]}]' for fn in fns)
        # Combined backlinks
        all_backlinks = []
        for fn in fns:
            all_backlinks.extend(fn['backlinks'])
        backlinks_html = ' '.join(all_backlinks)

        # Use the first footnote's id as the anchor
        primary_id = fns[0]['id']

        new_items.append(
            f'<li id="{primary_id}" class="compact-fn" value="{fns[0]["num"]}">'
            f'<p><strong class="fn-nums">{nums_label}</strong> '
            f'{text} {backlinks_html}</p></li>'
        )

    # Build replacement section
    new_section = (
        f'{section_open}\n<hr />\n<ol class="compact-footnotes">\n'
        + '\n'.join(new_items)
        + '\n</ol>\n</section>'
    )

    # Replace original section
    html = html[:section_match.start()] + new_section + html[section_match.end():]

    # Redirect in-text links: footnotes that merged into another need
    # their href targets updated.  E.g. if fn4 merged into fn1's entry,
    # the <a href="#fn4"> in the text should now point to #fn1.
    for text, fns in groups.items():
        if len(fns) > 1:
            primary_id = fns[0]['id']
            for fn in fns[1:]:
                html = html.replace(
                    f'href="#{fn["id"]}"',
                    f'href="#{primary_id}"')

    return html


def strip_header_pattern(html, pattern):
    """Strip a regex pattern (H2 through first HR) from pandoc HTML output."""
    html = re.sub(
        rf'<h2[^>]*>{pattern}</h2>'
        r'.*?<hr\s*/?\s*>\s*',
        '', html, count=1, flags=re.DOTALL)
    return html


def strip_sections_by_title(html, section_titles):
    """Remove H2 sections with matching titles (up to next H2 or end)."""
    for title in section_titles:
        html = re.sub(
            rf'<h2[^>]*>{re.escape(title)}</h2>.*?(?=<h2|$)',
            '', html, count=1, flags=re.DOTALL)
    return html


def process_svg_replacements(html, replacements, base_dir):
    """Replace ASCII art blocks with SVG diagrams based on config."""
    for repl in replacements:
        ascii_pattern = repl.get("ascii_pattern", r'<pre><code>┌─.*?</code></pre>')
        svg_file = repl.get("svg_file")
        if not svg_file:
            continue

        svg_path = base_dir / svg_file
        if not svg_path.exists():
            print(f"  WARNING: SVG file not found: {svg_path}")
            continue

        svg_content = svg_path.read_text(encoding="utf-8")
        replacement_html = f'<div class="diagram-container">\n{svg_content}\n</div>'
        html = re.sub(ascii_pattern, replacement_html, html, flags=re.DOTALL)

        # Process diagram notes if pattern provided
        notes_pattern = repl.get("notes_pattern")
        if notes_pattern:
            match = re.search(notes_pattern, html, re.DOTALL)
            if match:
                content = match.group(1)
                items = re.split(r' - (?=[A-Z])', content)
                notes_html = '<div class="diagram-notes">\n'
                notes_html += (
                    '<p style="margin: 0 0 6pt 0; font-weight: 600; '
                    'color: #2c3e50;">Diagram Notes:</p>\n'
                    '<ul style="margin: 0; padding-left: 16pt;">\n'
                )
                for item in items:
                    item = item.strip()
                    if item:
                        notes_html += f'<li>{item}</li>\n'
                notes_html += '</ul>\n</div>'
                html = re.sub(notes_pattern, notes_html, html, flags=re.DOTALL)

    return html


def renumber_sections(html, chapter_num):
    """Renumber H2 and H3 sections with chapter-prefixed numbers.

    Converts:
      <h2>1. Executive Summary</h2>   ->  <h2>C.1 Executive Summary</h2>
      <h2>4A. Live Licence Data</h2>  ->  <h2>C.N Live Licence Data</h2>
      <h2>Appendix A: Title</h2>      ->  <h2>C.N Title</h2>
      <h3>3.1 Sub Title</h3>          ->  <h3>C.N.M Sub Title</h3>
    """
    section_counter = [0]
    number_map = {}

    def replace_h2(match):
        attrs = match.group(1)
        content = match.group(2).strip()

        num_match = re.match(r'(\d+[A-Za-z]?)\.\s+(.*)', content, re.DOTALL)
        if num_match:
            old_num = num_match.group(1)
            title = num_match.group(2)
            section_counter[0] += 1
            number_map[old_num] = section_counter[0]
            return f'<h2{attrs}>{chapter_num}.{section_counter[0]} {title}</h2>'

        appendix_match = re.match(r'Appendix\s+[A-Z]:\s+(.*)', content, re.DOTALL)
        if appendix_match:
            title = appendix_match.group(1)
            section_counter[0] += 1
            return f'<h2{attrs}>{chapter_num}.{section_counter[0]} {title}</h2>'

        return match.group(0)

    html = re.sub(r'<h2([^>]*)>(.*?)</h2>', replace_h2, html, flags=re.DOTALL)

    def replace_h3(match):
        attrs = match.group(1)
        content = match.group(2).strip()

        num_match = re.match(r'(\d+)\.(\d+)\s+(.*)', content, re.DOTALL)
        if num_match:
            old_major = num_match.group(1)
            old_minor = num_match.group(2)
            title = num_match.group(3)
            if old_major in number_map:
                new_section = number_map[old_major]
                return (
                    f'<h3{attrs}>{chapter_num}.{new_section}.{old_minor}'
                    f' {title}</h3>'
                )
        return match.group(0)

    html = re.sub(r'<h3([^>]*)>(.*?)</h3>', replace_h3, html, flags=re.DOTALL)

    return html


def prefix_ids(html, chapter_num):
    """Prefix HTML ids with chapter number to avoid collisions.

    Preserves SVG content untouched — SVGs use internal id references
    (url(#id), xlink:href) that would break if ids were prefixed.
    """
    svgs = []

    def save_svg(match):
        svgs.append(match.group(0))
        return f'__SVG_PLACEHOLDER_{len(svgs) - 1}__'

    html = re.sub(r'<svg[\s>].*?</svg>', save_svg, html, flags=re.DOTALL)

    html = re.sub(
        r'id="([^"]+)"',
        lambda m: f'id="ch{chapter_num}-{m.group(1)}"',
        html)

    for i, svg in enumerate(svgs):
        html = html.replace(f'__SVG_PLACEHOLDER_{i}__', svg)

    return html


def _inline_list_to_html(p_tag):
    """Convert pandoc's inline '- item - item' format to a proper HTML list."""
    match = re.match(
        r'<p><strong>Next Steps:</strong>\s*(.*?)</p>', p_tag, re.DOTALL)
    if not match:
        return p_tag
    content = match.group(1).strip()
    if not content.startswith('-'):
        return p_tag
    items = re.split(r'\s+-\s+', content.lstrip('- '))
    result = '<p><strong>Next Steps:</strong></p>\n<ul>\n'
    for item in items:
        item = item.strip()
        if item:
            result += f'<li>{item}</li>\n'
    result += '</ul>'
    return result


def extract_end_matter(html):
    """Extract Document Control, Next Steps, References from chapter HTML.

    Returns: (body, references, doc_control_table, next_steps, notes)
    """
    references = ""
    doc_control = ""
    next_steps = ""
    notes = ""

    # Extract references div
    ref_match = re.search(
        r'\s*<div class="section-references">.*?</div>\s*',
        html, re.DOTALL)
    if ref_match:
        references = ref_match.group(0).strip()
        html = html[:ref_match.start()] + html[ref_match.end():]

    # Extract Document Control block and everything after it
    dc_match = re.search(
        r'\s*(?:<hr\s*/?\s*>\s*)?<p><strong>Document Control</strong></p>\s*(.*)',
        html, re.DOTALL)
    if dc_match:
        end_block = dc_match.group(1)
        html = html[:dc_match.start()].rstrip()

        table_match = re.search(r'<table>.*?</table>', end_block, re.DOTALL)
        if table_match:
            doc_control = table_match.group(0)

        # Next Steps — two pandoc formats depending on blank line in markdown
        ns_match = re.search(
            r'<p><strong>Next Steps:</strong></p>\s*<ul>.*?</ul>',
            end_block, re.DOTALL)
        if ns_match:
            next_steps = ns_match.group(0)
        else:
            ns_match = re.search(
                r'<p><strong>Next Steps:</strong>\s+.*?</p>',
                end_block, re.DOTALL)
            if ns_match:
                next_steps = _inline_list_to_html(ns_match.group(0))

        note_match = re.search(
            r'<p><strong>Note:</strong>.*?</p>',
            end_block, re.DOTALL)
        if note_match:
            notes = note_match.group(0)

    # Clean trailing <hr>s
    html = re.sub(r'\s*<hr\s*/?\s*>\s*$', '', html)

    return html, references, doc_control, next_steps, notes


def build_appendices(chapters_data):
    """Build consolidated appendix sections from extracted end matter."""

    # Appendix A: Source References
    ref_items = []
    for ch in chapters_data:
        if ch["references"]:
            ref_items.append(f"""
            <h3>Chapter {ch['chapter_num']}: {ch['title']}</h3>
            {ch['references']}""")

    appendix_a = f"""
    <div class="appendix-divider" id="appendix-a">
        <h1>Appendix A: Source References</h1>
        <div class="chapter-subtitle">Consolidated source citations from all chapters</div>
    </div>
    <div class="chapter-body appendix-body">
        {''.join(ref_items) if ref_items else '<p><em>No source references recorded.</em></p>'}
    </div>"""

    # Appendix B: Next Steps and Open Items
    ns_items = []
    for ch in chapters_data:
        parts = []
        if ch["next_steps"]:
            parts.append(ch["next_steps"])
        if ch["notes"]:
            parts.append(ch["notes"])
        if parts:
            ns_items.append(f"""
            <h3>Chapter {ch['chapter_num']}: {ch['title']}</h3>
            {''.join(parts)}""")

    appendix_b = f"""
    <div class="appendix-divider" id="appendix-b">
        <h1>Appendix B: Next Steps and Open Items</h1>
        <div class="chapter-subtitle">Consolidated action items and notes from all chapters</div>
    </div>
    <div class="chapter-body appendix-body">
        {''.join(ns_items) if ns_items else '<p><em>No next steps recorded.</em></p>'}
    </div>"""

    # Appendix C: Document History
    dc_items = []
    for ch in chapters_data:
        if ch["doc_control"]:
            dc_items.append(f"""
            <h3>Chapter {ch['chapter_num']}: {ch['title']} ({ch['id']}) — {ch['version']}</h3>
            {ch['doc_control']}""")

    appendix_c = f"""
    <div class="appendix-divider" id="appendix-c">
        <h1>Appendix C: Document History</h1>
        <div class="chapter-subtitle">Version history for all chapters</div>
    </div>
    <div class="chapter-body appendix-body">
        {''.join(dc_items) if dc_items else '<p><em>No version history recorded.</em></p>'}
    </div>"""

    return appendix_a + appendix_b + appendix_c


# ── HTML assembly ────────────────────────────────────────────────────

def build_info_block(config, theme=None):
    """Build the metadata info block HTML for a single document."""
    title = f"{config.get('title_line1', '')} {config.get('title_line2', '')}".strip()
    doc_id = config.get("doc_id", "")
    if doc_id:
        title = f"{doc_id}: {title}"
    doc_type = config.get("doc_type", "Report")
    version = config.get("version", "")
    classification = normalise_classification(
        config.get("classification", DEFAULTS["classification"])
    ).strip("[]")
    author = config.get("author", DEFAULTS["author"])
    org_name = theme.org("name") if theme else ""

    return f"""
    <div class="info-block">
        <h1 class="doc-title">{title}</h1>
        <p class="doc-subtitle">{org_name}</p>
        <div class="doc-meta">
            <p><strong>Company:</strong> {org_name}</p>
            <p><strong>Document Type:</strong> {doc_type}</p>
            <p><strong>Classification:</strong> {classification}</p>
            <p><strong>Version:</strong> {version}</p>
            <p><strong>Date:</strong> {datetime.date.today().strftime('%B %Y')}</p>
            <p><strong>Author:</strong> {author}</p>
        </div>
        <hr class="divider">
    </div>
    """


DISTRIBUTION_NOTICES = {
    "RESTRICTED": "Not for distribution outside review team",
    "INTERNAL": "For internal use only",
    "CONFIDENTIAL": "For designated recipients only",
    "PUBLIC": "",
}


def get_distribution_notice(config):
    """Get the distribution notice text based on classification or explicit override."""
    # Explicit override takes priority
    notice = config.get("distribution_notice")
    if notice is not None:
        return notice
    # Otherwise derive from classification
    classification = normalise_classification(
        config.get("classification", DEFAULTS["classification"])
    ).strip("[]")
    return DISTRIBUTION_NOTICES.get(classification, "")


def build_footer(config, theme=None):
    """Build the document footer HTML."""
    title = f"{config.get('title_line1', '')} {config.get('title_line2', '')}".strip()
    classification = normalise_classification(
        config.get("classification", DEFAULTS["classification"])
    ).strip("[]")
    notice = get_distribution_notice(config)
    notice_text = f" — {notice}" if notice else ""

    org_name = theme.org("name") if theme else ""
    secondary = theme.colour("secondary") if theme else "#34495e"

    # Support extra footer lines from config
    extra_lines = config.get("footer_extra_lines", [])
    extra_html = ""
    for line in extra_lines:
        extra_html += f'\n            <p style="margin-top: 6pt; font-style: italic;">{line}</p>'

    return f"""
        <div class="doc-footer">
            <p><strong style="color: {secondary};">{org_name}</strong> — {title}</p>
            <p>Classification: {classification.upper()}{notice_text}</p>{extra_html}
        </div>
    """


def assemble_single_html(config, body_html, theme=None):
    """Assemble a complete single-document HTML file."""
    org_short = theme.org("short_name") if theme else ""

    # Cover page
    cover_html = ""
    blank_verso = ""
    if config.get("cover", True):
        cover_html = create_cover_html(
            title_line1=config.get("title_line1", DEFAULTS["title_line1"]).upper(),
            title_line2=config.get("title_line2", DEFAULTS["title_line2"]).upper(),
            subtitle=config.get("subtitle", DEFAULTS["subtitle"]).upper(),
            author=config.get("author", DEFAULTS["author"]).upper(),
            year=config.get("year", DEFAULTS["year"]),
            classification=normalise_classification(
                config.get("classification", DEFAULTS["classification"])
            ),
            version=config.get("version", DEFAULTS["version"]),
            theme=theme,
        )
        blank_verso = """
    <div class="blank-verso">
        <p>This page is intentionally blank.</p>
    </div>"""

    # Info block
    info_block = ""
    if config.get("info_block", True):
        info_block = build_info_block(config, theme=theme)

    # CSS
    title = f"{config.get('title_line1', '')} {config.get('title_line2', '')}".strip()
    doc_title = config.get("doc_title", f"{org_short} — {title}")
    classification = normalise_classification(
        config.get("classification", DEFAULTS["classification"])
    )
    css = get_full_css(
        include_toc=config.get("toc", True),
        include_info_block=config.get("info_block", True),
        doc_title=doc_title,
        classification=classification,
        theme=theme,
    )

    footer = build_footer(config, theme=theme)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — {org_short}</title>
    <style>
        {css}
    </style>
</head>
<body>
    {cover_html}
    {blank_verso}
    <div class="content-wrapper">
        {info_block}
        {body_html}
        {footer}
    </div>
</body>
</html>"""


def assemble_combined_html(config, chapters_html, front_matter_html="",
                           appendices_html="", theme=None):
    """Assemble a complete multi-chapter combined HTML file."""
    org_short = theme.org("short_name") if theme else ""
    cover_section = config.get("cover", {})

    cover_html = create_cover_html(
        title_line1=cover_section.get("title_line1", DEFAULTS["title_line1"]).upper(),
        title_line2=cover_section.get("title_line2", DEFAULTS["title_line2"]).upper(),
        subtitle=cover_section.get("subtitle", DEFAULTS["subtitle"]).upper(),
        author=cover_section.get("author", DEFAULTS["author"]).upper(),
        year=cover_section.get("year", DEFAULTS["year"]),
        classification=normalise_classification(
            cover_section.get("classification", DEFAULTS["classification"])
        ),
        version=cover_section.get("version", DEFAULTS["version"]),
        theme=theme,
    )

    doc_title = config.get("doc_title", f"{org_short} — Combined Document")
    classification_raw = normalise_classification(
        cover_section.get("classification", DEFAULTS["classification"])
    )

    # Determine whether appendix CSS is needed
    has_appendices = bool(appendices_html)

    css = get_full_css(
        include_chapter_dividers=True,
        include_appendix_dividers=has_appendices,
        doc_title=doc_title,
        classification=classification_raw,
        theme=theme,
    )

    # Build footer using the cover section as config (with fallback defaults)
    footer_config = dict(DEFAULTS)
    footer_config.update(cover_section)
    # Pass through footer_extra_lines from top-level config
    if config.get("footer_extra_lines"):
        footer_config["footer_extra_lines"] = config["footer_extra_lines"]
    footer = build_footer(footer_config, theme=theme)

    html_title = config.get("html_title", doc_title)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{html_title}</title>
    <style>
        {css}
    </style>
</head>
<body>
    {cover_html}
    <div class="blank-verso">
        <p>This page is intentionally blank.</p>
    </div>
    <div class="content-wrapper">
        {front_matter_html}
        {chapters_html}
        {appendices_html}
        {footer}
    </div>
</body>
</html>"""


# ── PDF rendering ────────────────────────────────────────────────────

def render_pdf(html_path, pdf_path=None):
    """Render an HTML file to PDF using WeasyPrint."""
    try:
        from weasyprint import HTML
    except ImportError:
        print("  ERROR: weasyprint not installed.")
        print("  Run: source venv/bin/activate && pip install weasyprint")
        return False

    if pdf_path is None:
        pdf_path = html_path.with_suffix(".pdf")

    html = HTML(filename=str(html_path), base_url=str(html_path.parent))
    html.write_pdf(str(pdf_path))

    size_kb = pdf_path.stat().st_size / 1024
    if size_kb > 1024:
        print(f"  PDF: {pdf_path.name} ({size_kb / 1024:.1f} MB)")
    else:
        print(f"  PDF: {pdf_path.name} ({size_kb:.0f} KB)")
    return True


# ── init subcommand ──────────────────────────────────────────────────

def cmd_init(args):
    """Scaffold a new document or config file."""

    # Config file mode
    if args.config:
        return init_config(args)

    # Single document mode
    return init_document(args)


def init_document(args):
    """Create a skeleton markdown file with YAML front-matter."""
    output_path = Path(args.output)
    if output_path.exists():
        print(f"  ERROR: {output_path} already exists. Remove it first or choose another name.")
        return False

    title1 = args.title1 or DEFAULTS["title_line1"]
    title2 = args.title2 or DEFAULTS["title_line2"]
    subtitle = args.subtitle or DEFAULTS["subtitle"]
    version = args.version or DEFAULTS["version"]
    doc_type = args.doc_type or DEFAULTS["doc_type"]
    classification = args.classification or DEFAULTS["classification"]
    author = args.author or DEFAULTS["author"]
    year = args.year or DEFAULTS["year"]
    today = datetime.date.today().strftime("%B %Y")

    # Derive a heading from the title
    heading = f"{title1.title()} {title2.title()}".strip()

    content = f"""---
# ── phoenix-docgen front-matter ─────────────────────────────────────
# All fields are optional. CLI flags (--version, --title1, etc.)
# override these values. Run 'phoenix-docgen help frontmatter' for
# the full field reference.

title_line1: "{title1}"           # Cover page title — line 1 (uppercased on cover)
title_line2: "{title2}"           # Cover page title — line 2
subtitle: "{subtitle}"            # Cover subtitle (uppercased on cover)
version: "{version}"              # Version shown on cover and info block
doc_type: "{doc_type}"            # Document type in info block (e.g. Report, Assessment)
classification: "{classification}"  # [RESTRICTED] | [INTERNAL] | [CONFIDENTIAL] | [PUBLIC]
author: "{author}"
year: "{year}"

toc: true                          # Table of contents (true/false)
toc_depth: 3                       # Heading depth for TOC (1–6)
info_block: true                   # Metadata block after cover (true/false)
cover: true                        # Cover page and blank verso (true/false)

# ── Optional fields (uncomment to use) ──────────────────────────────
# doc_title: "Custom Page Footer Title"   # Override centre page footer text
# doc_id: "A1"                            # Document ID prefix
# distribution_notice: "Custom notice"    # Override auto distribution notice
# footer_extra_lines:                     # Extra lines in document footer
#   - "Distribution: Review team only"
# header_pattern: "^Pattern.*"            # Regex to strip from pandoc output
---

# {heading}

*Replace this with your document content.*

<!-- ─── Authoring tips ──────────────────────────────────────────────
  Run 'phoenix-docgen help markdown' for the full authoring reference.

  ALERTS — GitHub-style callout boxes:
    > [!NOTE]
    > Informational content.

    > [!WARNING]
    > Potential issue.

    Types: [!NOTE] [!TIP] [!IMPORTANT] [!WARNING] [!CAUTION]

  PAGE BREAKS:
    <div style="page-break-after: always; break-after: page;"></div>

  LANDSCAPE PAGES — for wide tables:
    <div class="landscape-section">
    | Wide | Table | Here |
    | ... | ... | ... |
    </div>

  FOOTNOTES:
    Inline reference[^1], with definition at bottom of file.
    [^1]: Source citation here.
    Duplicate footnotes are automatically compacted.
───────────────────────────────────────────────────────────────────── -->

## 1. Executive Summary

## 2. Background and Context

## 3. Analysis

## 4. Recommendations

---

**Document Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1     | {today} | Tech Lead / Architect | Initial draft |
"""

    output_path.write_text(content, encoding="utf-8")
    print(f"  Created: {output_path}")
    print(f"  Edit the file, then build with: phoenix-docgen build {output_path} --pdf")
    return True


def init_config(args):
    """Create a skeleton YAML config file for multi-chapter documents."""
    output_path = Path(args.config)
    if output_path.exists():
        print(f"  ERROR: {output_path} already exists. Remove it first or choose another name.")
        return False

    title1 = args.title1 or DEFAULTS["title_line1"]
    title2 = args.title2 or DEFAULTS["title_line2"]

    # Build chapters list
    chapters = []
    if args.chapters:
        for i, ch_file in enumerate(args.chapters, 1):
            ch_path = Path(ch_file)
            # Derive title from filename
            title = ch_path.stem.replace("-", " ").replace("_", " ").title()
            chapters.append({
                "id": f"Ch{i}",
                "title": title,
                "source": str(ch_file),
                "version": "v0.1",
            })
    else:
        chapters = [
            {"id": "Ch1", "title": "Chapter One Title", "source": "chapter-one.md", "version": "v0.1"},
            {"id": "Ch2", "title": "Chapter Two Title", "source": "chapter-two.md", "version": "v0.1"},
        ]

    # Derive output name from config filename
    output_name = output_path.stem.replace("-config", "").replace("_config", "")
    output_name = f"{output_name}-Combined.html"

    theme = getattr(args, '_theme', None)
    org_short = theme.org("short_name") if theme else ""

    config = {
        "cover": {
            "title_line1": title1,
            "title_line2": title2,
            "subtitle": args.subtitle or DEFAULTS["subtitle"],
            "version": args.version or DEFAULTS["version"],
            "author": args.author or DEFAULTS["author"],
            "classification": args.classification or DEFAULTS["classification"],
            "year": args.year or DEFAULTS["year"],
        },
        "doc_title": f"{title1} {title2} — {org_short}".strip(),
        "chapters": chapters,
        "output": output_name,
    }

    # Build chapters YAML block
    chapters_yaml = ""
    for ch in chapters:
        chapters_yaml += f"""
  - id: "{ch['id']}"
    title: "{ch['title']}"
    source: "{ch['source']}"
    version: "{ch['version']}"
    # strip_sections:           # H2 titles to remove from this chapter
    #   - "Internal Notes"
    # svg_replacements:         # Replace ASCII art with SVG diagrams
    #   - ascii_pattern: '<pre><code>.*?diagram.*?</code></pre>'
    #     svg_file: "diagrams/overview.svg"
"""

    cover = config["cover"]
    yaml_content = f"""# ── phoenix-docgen combined document configuration ──────────────────
# Generated: {datetime.date.today().isoformat()}
# Build with: phoenix-docgen combine --config {output_path} --pdf
# Full reference: phoenix-docgen help combine
# ─────────────────────────────────────────────────────────────────────

# ── Cover page metadata ─────────────────────────────────────────────
# Same fields as single-document front-matter.
# See: phoenix-docgen help frontmatter

cover:
  title_line1: "{cover['title_line1']}"
  title_line2: "{cover['title_line2']}"
  subtitle: "{cover['subtitle']}"
  version: "{cover['version']}"
  author: "{cover['author']}"
  classification: "{cover['classification']}"
  year: "{cover['year']}"

# ── Document-level settings ─────────────────────────────────────────

doc_title: "{config['doc_title']}"   # Centre page footer text
output: "{config['output']}"         # Output filename

# distribution_notice: "Custom notice"    # Override auto notice
# footer_extra_lines:                     # Extra lines in document footer
#   - "Distribution: Review team only"
# html_title: "Browser Tab Title"         # Override <title> element
# header_pattern: "^Pattern.*"            # Regex to strip from all chapters

# ── Front matter (optional) ─────────────────────────────────────────
# Raw HTML inserted between cover and first chapter (e.g. master TOC).
#
# front_matter_html: |
#   <div class="master-toc">
#     <h2>Contents</h2>
#     <p>Chapter listing...</p>
#   </div>

# ── Chapters ────────────────────────────────────────────────────────
# Each chapter needs at minimum a 'source' path (relative to this
# config file). Other fields are optional.
#
# Fields: id, title, source, version, chapter_num, strip_sections,
#         svg_replacements

chapters:{chapters_yaml}
# ── Processing options (all default to false/empty) ─────────────────
# Uncomment and set to true to enable advanced features.
# See: phoenix-docgen help combine

# options:
#   renumber_sections: false      # Prefix H2/H3 with chapter numbers (3.1, 3.1.1)
#   extract_end_matter: false     # Pull out Document Control, Next Steps, References
#   build_appendices: false       # Create consolidated Appendices A, B, C
#   prefix_ids: false             # Prefix HTML ids to avoid collisions (ch1-title)
#   strip_sections:               # Remove named H2 sections from all chapters
#     - "Internal Notes"
#   chapter_format: "{{id}}: {{title}}"   # Chapter divider heading format
#   chapter_subtitle: ""                  # Chapter divider subtitle format
"""

    output_path.write_text(yaml_content, encoding="utf-8")
    print(f"  Created: {output_path}")
    print(f"  Edit the config, then build with: phoenix-docgen combine --config {output_path} --pdf")
    return True


# ── build subcommand ─────────────────────────────────────────────────

def cmd_build(args):
    """Build a single document from markdown to HTML (and optionally PDF)."""
    source_path = Path(args.source)
    if not source_path.exists():
        print(f"  ERROR: Source not found: {source_path}")
        return False

    print(f"  Building: {source_path.name}")

    # Parse front-matter
    front_matter, body = parse_front_matter(source_path)

    # CLI overrides
    cli = {}
    for key in ["title1", "title2", "subtitle", "version", "author",
                 "classification", "year", "doc_type", "doc_title", "doc_id"]:
        val = getattr(args, key, None)
        if val is not None:
            # Map CLI names to config names
            config_key = {
                "title1": "title_line1",
                "title2": "title_line2",
            }.get(key, key)
            cli[config_key] = val

    if args.no_toc:
        cli["toc"] = False
    if args.no_info_block:
        cli["info_block"] = False
    if args.no_cover:
        cli["cover"] = False

    config = merge_config(DEFAULTS, front_matter, cli)

    # Convert markdown body to HTML
    body_html = convert_body_to_html(
        body,
        toc=config.get("toc", True),
        toc_depth=config.get("toc_depth", 3),
    )
    if body_html is None:
        return False

    # Strip header pattern if configured
    pattern = args.header_pattern or config.get("header_pattern")
    if pattern:
        body_html = strip_header_pattern(body_html, pattern)

    # SVG replacements if configured
    svg_replacements = config.get("svg_replacements", [])
    if svg_replacements:
        body_html = process_svg_replacements(
            body_html, svg_replacements, source_path.parent)

    # Process GitHub-style alerts
    body_html = process_alerts(body_html)

    # Compact duplicate footnotes
    body_html = compact_footnotes(body_html)

    # Assemble
    theme = getattr(args, '_theme', None)
    html = assemble_single_html(config, body_html, theme=theme)

    # Write HTML
    if args.output:
        output_path = Path(args.output)
    else:
        output_path = source_path.with_suffix(".html")

    output_path.write_text(html, encoding="utf-8")
    size_kb = output_path.stat().st_size / 1024
    print(f"  HTML: {output_path.name} ({size_kb:.0f} KB)")

    # Determine whether to keep HTML: explicit --html, or no --pdf means HTML-only
    keep_html = args.html or not args.pdf

    # Render PDF if requested
    if args.pdf:
        pdf_path = output_path.with_suffix(".pdf")
        render_pdf(output_path, pdf_path)

    # Clean up intermediate HTML unless we're keeping it
    if not keep_html:
        output_path.unlink(missing_ok=True)

    return True


# ── combine subcommand ───────────────────────────────────────────────

def cmd_combine(args):
    """Build a multi-chapter combined document from a YAML config."""
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"  ERROR: Config not found: {config_path}")
        return False

    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not config:
        print("  ERROR: Config file is empty")
        return False

    chapters = config.get("chapters", [])
    if not chapters:
        print("  ERROR: No chapters defined in config")
        return False

    cover = config.get("cover", {})
    header_pattern = config.get("header_pattern")
    config_dir = config_path.parent

    # Combined document options
    options = config.get("options", {})
    do_renumber = options.get("renumber_sections", False)
    do_extract = options.get("extract_end_matter", False)
    do_appendices = options.get("build_appendices", False)
    do_prefix_ids = options.get("prefix_ids", False)
    global_strip_sections = options.get("strip_sections", [])
    chapter_format = options.get("chapter_format", "{id}: {title}")
    chapter_subtitle_fmt = options.get("chapter_subtitle", "")

    print(f"  Combining {len(chapters)} chapters from: {config_path.name}")

    # Build each chapter
    chapters_html = ""
    chapters_data = []

    for i, ch in enumerate(chapters, 1):
        source_path = config_dir / ch["source"]
        if not source_path.exists():
            print(f"  SKIP: {ch.get('id', f'Ch{i}')} — {ch['source']} not found")
            continue

        ch_id = ch.get("id", f"Ch{i}")
        ch_title = ch.get("title", source_path.stem)
        ch_version = ch.get("version", "")
        ch_num = ch.get("chapter_num", i)

        print(f"  Converting {ch_id}: {source_path.name}")

        body = convert_md_to_html(source_path)
        if body is None:
            continue

        # SVG replacements (per-chapter)
        svg_replacements = ch.get("svg_replacements", [])
        if svg_replacements:
            body = process_svg_replacements(body, svg_replacements, config_dir)

        # Strip H1 (title) — the chapter divider replaces it
        body = re.sub(r'^<h1[^>]*>.*?</h1>', '', body, count=1, flags=re.DOTALL)

        # Strip header pattern if configured
        if header_pattern:
            body = strip_header_pattern(body, header_pattern)

        # Strip sections by title (per-chapter + global)
        sections_to_strip = global_strip_sections + ch.get("strip_sections", [])
        if sections_to_strip:
            body = strip_sections_by_title(body, sections_to_strip)

        # Process GitHub-style alerts
        body = process_alerts(body)

        # Compact duplicate footnotes (before extraction)
        body = compact_footnotes(body)

        # Extract end matter before renumbering
        references = ""
        doc_control = ""
        next_steps = ""
        notes = ""
        if do_extract:
            body, references, doc_control, next_steps, notes = (
                extract_end_matter(body))

        # Renumber sections with chapter prefix
        if do_renumber:
            body = renumber_sections(body, ch_num)

        # Prefix ids to avoid collisions between chapters
        if do_prefix_ids:
            body = prefix_ids(body, ch_num)

        # Store extracted end matter for appendices
        if do_extract:
            chapters_data.append({
                "id": ch_id,
                "chapter_num": ch_num,
                "title": ch_title,
                "version": ch_version,
                "references": references,
                "doc_control": doc_control,
                "next_steps": next_steps,
                "notes": notes,
            })

        # Build chapter divider
        divider_title = chapter_format.format(
            id=ch_id, title=ch_title, num=ch_num)
        divider_subtitle = chapter_subtitle_fmt.format(
            id=ch_id, title=ch_title, num=ch_num) if chapter_subtitle_fmt else ""

        # Chapter meta line
        meta_parts = []
        if ch_version:
            meta_parts.append(f"Version {ch_version} (Draft)")
        meta_parts.append(datetime.date.today().strftime("%B %Y"))
        classification = normalise_classification(
            cover.get("classification", DEFAULTS["classification"])
        ).strip("[]")
        meta_parts.append(f"Classification: {classification}")
        meta_line = " · ".join(meta_parts)

        # Use chapter_num for the anchor id
        divider_id = ch.get("divider_id", f"chapter-{ch_num}")

        chapters_html += f"""
        <div class="chapter-divider" id="{divider_id}">
            <h1>{divider_title}</h1>
            <div class="chapter-subtitle">{divider_subtitle}</div>
            <div class="chapter-meta">{meta_line}</div>
        </div>

        <div class="chapter-body">
            {body}
        </div>
        """

    # Build appendices from extracted end matter
    appendices_html = ""
    if do_appendices and chapters_data:
        print("  Building appendices...")
        appendices_html = build_appendices(chapters_data)

    # Front matter HTML (optional, from config)
    front_matter_html = config.get("front_matter_html", "")

    # Assemble
    theme = getattr(args, '_theme', None)
    html = assemble_combined_html(
        config, chapters_html, front_matter_html, appendices_html, theme=theme)

    # Write HTML
    if args.output:
        output_path = Path(args.output)
    else:
        output_name = config.get("output", config_path.stem + "-Combined.html")
        output_path = config_dir / output_name

    output_path.write_text(html, encoding="utf-8")
    size_kb = output_path.stat().st_size / 1024
    if size_kb > 1024:
        print(f"  HTML: {output_path.name} ({size_kb / 1024:.1f} MB)")
    else:
        print(f"  HTML: {output_path.name} ({size_kb:.0f} KB)")

    # Determine whether to keep HTML: explicit --html, or no --pdf means HTML-only
    keep_html = args.html or not args.pdf

    # Render PDF if requested
    if args.pdf:
        pdf_path = output_path.with_suffix(".pdf")
        render_pdf(output_path, pdf_path)

    # Clean up intermediate HTML unless we're keeping it
    if not keep_html:
        output_path.unlink(missing_ok=True)

    return True


# ── CLI argument parsing ─────────────────────────────────────────────

def build_parser():
    """Build the argparse parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="phoenix-docgen",
        description="Branded document builder — markdown to styled HTML/PDF with configurable themes.",
        epilog=textwrap.dedent("""\
            examples:
              phoenix-docgen init report.md --title1 "APPLICATION" --title2 "STRATEGY"
              phoenix-docgen init --config project.yaml --chapters intro.md analysis.md
              phoenix-docgen build report.md --pdf
              phoenix-docgen build report.md --theme mytheme --version "v2.0 DRAFT" --pdf
              phoenix-docgen combine --config project.yaml --pdf
        """),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # ── init ──
    init_parser = subparsers.add_parser(
        "init",
        help="Scaffold a new document or config file with defaults",
        description="Create a skeleton markdown file with YAML front-matter, or a YAML config for multi-chapter builds.",
    )
    init_parser.add_argument("output", nargs="?", help="Output markdown file path")
    init_parser.add_argument("--config", help="Create a YAML config file instead of a markdown file")
    init_parser.add_argument("--chapters", nargs="+", metavar="FILE", help="Markdown files to include as chapters (config mode)")
    _add_metadata_args(init_parser)

    # ── build ──
    build_parser = subparsers.add_parser(
        "build",
        help="Build a single document from markdown",
        description="Convert a markdown file (with optional YAML front-matter) to branded HTML and PDF.",
    )
    build_parser.add_argument("source", help="Source markdown file")
    build_parser.add_argument("--pdf", action="store_true", help="Generate PDF via WeasyPrint")
    build_parser.add_argument("--html", action="store_true", help="Keep HTML output (default if --pdf not given)")
    build_parser.add_argument("--output", "-o", help="Override output file path")
    build_parser.add_argument("--no-toc", action="store_true", help="Disable table of contents")
    build_parser.add_argument("--no-info-block", action="store_true", help="Disable metadata info block")
    build_parser.add_argument("--no-cover", action="store_true", help="Disable cover page")
    build_parser.add_argument("--header-pattern", metavar="REGEX", help="Regex pattern to strip from pandoc output (H2 through first HR)")
    _add_metadata_args(build_parser)

    # ── combine ──
    combine_parser = subparsers.add_parser(
        "combine",
        help="Build a multi-chapter document from a YAML config",
        description="Combine multiple markdown files into a single branded document with chapter dividers.",
    )
    combine_parser.add_argument("--config", required=True, help="YAML configuration file")
    combine_parser.add_argument("--pdf", action="store_true", help="Generate PDF via WeasyPrint")
    combine_parser.add_argument("--html", action="store_true", help="Keep HTML output (default if --pdf not given)")
    combine_parser.add_argument("--output", "-o", help="Override output file path")

    # ── help ──
    help_parser = subparsers.add_parser(
        "help",
        help="Show detailed help on a specific topic",
        description="Display comprehensive documentation for phoenix-docgen features.",
    )
    help_parser.add_argument(
        "topic", nargs="?", default=None,
        help="Help topic (run 'phoenix-docgen help' for full list)",
    )

    return parser


def _add_metadata_args(parser):
    """Add common metadata arguments to a subcommand parser."""
    group = parser.add_argument_group("metadata overrides")
    group.add_argument("--title1", metavar="TEXT", help="Cover title line 1")
    group.add_argument("--title2", metavar="TEXT", help="Cover title line 2")
    group.add_argument("--subtitle", metavar="TEXT", help="Cover subtitle")
    group.add_argument("--version", metavar="TEXT", help="Version field")
    group.add_argument("--author", metavar="TEXT", help="Author line")
    group.add_argument("--classification", metavar="TEXT", help="Classification (e.g. [RESTRICTED])")
    group.add_argument("--year", metavar="TEXT", help="Year for cover page")
    group.add_argument("--doc-type", metavar="TEXT", dest="doc_type", help="Document type (e.g. Report, Assessment)")
    group.add_argument("--doc-title", metavar="TEXT", dest="doc_title", help="Page footer document title")
    group.add_argument("--doc-id", metavar="TEXT", dest="doc_id", help="Document ID prefix (e.g. A1, Ch1)")

    theme_group = parser.add_argument_group("theme")
    theme_group.add_argument("--theme", metavar="NAME", help="Theme name (e.g. mytheme)")
    theme_group.add_argument("--themes-dir", metavar="PATH", dest="themes_dir", help="Path to themes directory")


# ── Main ─────────────────────────────────────────────────────────────

def main():
    global DEFAULTS

    parser = build_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "help":
        show_help(args.topic)
        sys.exit(0)

    # ── Resolve theme ────────────────────────────────────────────────
    global_config = load_config()
    themes_dir = resolve_themes_dir(
        cli_path=getattr(args, "themes_dir", None),
        config=global_config,
    )
    theme_name = getattr(args, "theme", None)
    theme = resolve_theme(name=theme_name, themes_dir=themes_dir, config=global_config)

    # Update module-level DEFAULTS with theme values
    DEFAULTS = get_defaults(theme)
    # Stash theme on args so subcommands can access it
    args._theme = theme

    if theme:
        print(f"phoenix-docgen — {args.command} (theme: {theme.display_name})")
    else:
        print(f"phoenix-docgen — {args.command}")
    print()

    if args.command == "init":
        if not args.output and not args.config:
            print("  ERROR: Provide an output file path, or use --config for a YAML config.")
            sys.exit(1)
        success = cmd_init(args)
    elif args.command == "build":
        success = cmd_build(args)
    elif args.command == "combine":
        success = cmd_combine(args)
    else:
        parser.print_help()
        sys.exit(1)

    print()
    if success:
        print("Done.")
    else:
        print("Failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()
