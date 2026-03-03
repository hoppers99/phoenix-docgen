"""
Topic-based help system for phoenix-docgen.

Each topic is a (title, body) tuple in the TOPICS dict. The show_help()
function is called from main() when `phoenix-docgen help [topic]` is invoked.

Maintenance note: when new features are added to phoenix-docgen.py or
shared_styles.py, update the relevant topic(s) here in parallel.
"""

import textwrap

# ── Overview (no-argument output) ────────────────────────────────────

OVERVIEW = textwrap.dedent("""\
    phoenix-docgen help — Comprehensive Documentation

    Usage:  phoenix-docgen help <topic>

    TOPICS

      frontmatter     YAML front-matter fields and defaults
      alerts          GitHub-style alert boxes and inline glyphs
      markdown        Markdown authoring features (landscape, page breaks,
                      footnotes, tables, raw HTML)
      combine         Multi-chapter document configuration (YAML config)
      cover           Cover page, SVG template, and logo
      classification  Classification levels and distribution notices
      landscape       Landscape sections and table column widths
      footer          Document footer customisation
      branding        Multi-branding and extensibility

    QUICK START

      phoenix-docgen init report.md                  # scaffold a document
      phoenix-docgen build report.md --pdf           # build to PDF
      phoenix-docgen init --config project.yaml      # scaffold a multi-chapter config
      phoenix-docgen combine --config project.yaml --pdf

    Run 'phoenix-docgen help <topic>' for detailed reference on any topic.
    Run 'phoenix-docgen <command> --help' for CLI flag reference.
""")


# ── Topic: frontmatter ───────────────────────────────────────────────

TOPIC_FRONTMATTER = (
    "YAML Front-Matter Reference",
    textwrap.dedent("""\
    Place YAML front-matter at the top of any markdown file between --- markers.
    All fields are optional; unspecified fields use sensible defaults.

    COMPLETE EXAMPLE

        ---
        title_line1: "APPLICATION"
        title_line2: "STRATEGY"
        subtitle: "ACME CORP"
        version: "v2.0 DRAFT"
        doc_type: "Strategy Framework"
        classification: "[CONFIDENTIAL]"
        author: "JANE SMITH — PRINCIPAL ARCHITECT"
        year: "2026"
        theme: mytheme
        toc: true
        toc_depth: 3
        info_block: true
        cover: true
        doc_title: "Application Strategy — Acme Corp"
        doc_id: "A1"
        # distribution_notice: "Custom notice text"
        # footer_extra_lines:
        #   - "Distribution: Review team only"
        # header_pattern: "^Scope.*"
        # svg_replacements:
        #   - ascii_pattern: '<pre><code>.*?diagram.*?</code></pre>'
        #     svg_file: "diagrams/overview.svg"
        ---

    FIELD REFERENCE

        Field                Type          Default
        ───────────────────  ────────────  ──────────────────────────────
        title_line1          string        "DOCUMENT"
        title_line2          string        "TITLE"
        subtitle             string        (from theme)
        version              string        "v0.1 DRAFT"
        doc_type             string        "Report"
        classification       string        "[RESTRICTED]"
        author               string        (from theme)
        year                 string        (current year)
        toc                  boolean       true
        toc_depth            integer       3
        info_block           boolean       true
        cover                boolean       true
        doc_title            string        (derived from title lines)
        doc_id               string        (none)
        distribution_notice  string        (auto from classification)
        footer_extra_lines   list[string]  []
        header_pattern       string        (none)
        svg_replacements     list[object]  []

    FIELD DETAILS

        title_line1, title_line2
            Two lines of the cover page title. Uppercased on the cover.
            Also used to derive doc_title if not set explicitly.

        subtitle
            Appears below the title on the cover page. Uppercased.

        version
            Shown on the cover page and in the info block. Use any
            format, e.g. "v0.1 DRAFT", "v2.0 FINAL — 10/03/2026".

        doc_type
            Document type shown in the info block (e.g. "Report",
            "Strategy Framework", "Risk Assessment"). Not on cover.

        classification
            Accepts any of: RESTRICTED, [RESTRICTED], "[RESTRICTED]",
            restricted — all normalised to [RESTRICTED]. Determines
            the page footer marker and auto distribution notice.
            See: phoenix-docgen help classification

        author
            Author line on cover page. Uppercased on cover.

        year
            Year badge on the cover page. Defaults to current year.

        toc / toc_depth
            Table of contents generation. toc_depth controls which
            heading levels are included (1–6, default 3 = H1–H3).

        info_block
            Metadata block after the cover page showing doc_type,
            classification, version, date, and author.

        cover
            Set to false (or use --no-cover) to omit the cover page
            and blank verso entirely.

        doc_title
            Text in the centre of every page footer. If not set,
            derived from title_line1 + title_line2.

        doc_id
            Short document ID prefix (e.g. "A1", "Ch1"). Used in
            multi-chapter mode for chapter divider labels.

        distribution_notice
            Override the auto-generated distribution notice in the
            footer. See: phoenix-docgen help classification

        footer_extra_lines
            List of extra lines added (in italics) to the document
            footer. See: phoenix-docgen help footer

        header_pattern
            Regex pattern to strip from pandoc output. Matches an H2
            element through the next HR and removes the block. Useful
            for removing auto-generated headers.

        svg_replacements
            List of objects with keys: ascii_pattern (regex to find
            ASCII art in HTML), svg_file (path to SVG replacement),
            and optional notes_pattern (regex to extract diagram notes).

    METADATA PRIORITY (highest wins)

        1. CLI arguments (--version, --title1, etc.)
        2. YAML front-matter in the markdown file
        3. Built-in defaults
    """),
)


# ── Topic: alerts ────────────────────────────────────────────────────

TOPIC_ALERTS = (
    "Alert Boxes and Inline Glyphs",
    textwrap.dedent("""\
    phoenix-docgen supports GitHub-style alert boxes in markdown, rendered
    as styled callout boxes with coloured borders and icons.

    BLOCK-LEVEL ALERTS

        Write alerts as blockquotes with a type marker on the first line:

        > [!NOTE]
        > Informational content the reader should be aware of.

        > [!TIP]
        > A helpful suggestion or best practice.

        > [!IMPORTANT]
        > Critical information the reader must not miss.

        > [!WARNING]
        > Potential issue that could cause problems.

        > [!CAUTION]
        > Dangerous action that could cause harm or data loss.

        Multi-paragraph alerts are supported:

        > [!WARNING]
        > First paragraph of the warning.
        >
        > Second paragraph with more detail.

    ALERT TYPES AND COLOURS

        Type          Colour    Icon
        ────────────  ────────  ──────────────────
        [!NOTE]       Blue      Circle with "i"
        [!TIP]        Green     Lightbulb
        [!IMPORTANT]  Purple    Circle with "!"
        [!WARNING]    Orange    Triangle with "!"
        [!CAUTION]    Red       Octagon with "!"

        Each alert gets a coloured left border (4pt), light grey
        background, a bold title with icon, and contained paragraphs.

    INLINE ALERT GLYPHS

        Place a type marker inline to insert a small coloured icon:

        This action [!WARNING] may cause data loss.
        Check the configuration [!IMPORTANT] before proceeding.

        Inline glyphs render as small (11pt) coloured icons matching
        the type's colour. They do not have a surrounding box.
    """),
)


# ── Topic: markdown ──────────────────────────────────────────────────

TOPIC_MARKDOWN = (
    "Markdown Authoring Features",
    textwrap.dedent("""\
    phoenix-docgen processes standard pandoc markdown with several
    additional features for professional document authoring.

    LANDSCAPE SECTIONS

        Wrap content in a landscape div to rotate pages to A4 landscape:

        <div class="landscape-section">

        ## Appendices

        | Column 1 | Column 2 | Column 3 |
        |----------|----------|----------|
        | data     | data     | data     |

        </div>

        Landscape pages use 15mm margins (vs 20mm portrait) and tables
        automatically get table-layout: fixed for column width control.

        See: phoenix-docgen help landscape

    PAGE BREAKS

        Force a page break between sections:

        <div style="page-break-after: always; break-after: page;"></div>

        Place this between any two blocks of content. The dual
        property (page-break-after + break-after) ensures compatibility
        across rendering engines.

    ALERTS AND CALLOUTS

        GitHub-style alert boxes with five types:

        > [!NOTE]
        > This is a note.

        See: phoenix-docgen help alerts

    FOOTNOTES

        Standard pandoc footnote syntax:

        This claim needs a source[^1].
        Another reference to the same source[^2].

        [^1]: Smith, J. (2025). Example Reference.
        [^2]: Smith, J. (2025). Example Reference.

        Duplicate footnotes with identical text are automatically
        compacted into combined entries showing all reference numbers
        (e.g. [1][2] Smith, J. ...).

    TABLES

        Standard markdown pipe tables:

        | Header 1 | Header 2 | Header 3 |
        |----------|----------|----------|
        | Cell     | Cell     | Cell     |
        | Cell     | Cell     | Cell     |

        Tables are styled with a dark header row (theme secondary colour,
        white text), light borders, and alternating row striping.

    RAW HTML

        Any HTML passes through pandoc into the output. This is useful
        for custom div wrappers, SVG diagrams, <br> tags, and special
        layout needs. Common uses:

        - Landscape sections (see above)
        - Page breaks (see above)
        - Custom styling via inline style attributes
        - Embedding SVG diagrams directly

    HEADINGS

        Use standard markdown headings. They are styled as:

        # H1  — 20pt, primary colour, used for document title
        ## H2 — 16pt, primary colour, with bottom border (main sections)
        ### H3 — 14pt, dark grey (subsections)
        #### H4 — 12pt, dark grey (sub-subsections)

        H2 and H3 headings are included in the table of contents
        by default (toc_depth: 3 includes H1–H3).

    BLOCKQUOTES

        Standard blockquotes (not alerts) are styled with a green
        left border (4pt) and light grey background:

        > This is a standard blockquote.
    """),
)


# ── Topic: combine ───────────────────────────────────────────────────

TOPIC_COMBINE = (
    "Multi-Chapter Document Configuration",
    textwrap.dedent("""\
    The 'combine' command assembles multiple markdown files into a
    single document with chapter dividers, driven by a YAML config.

    USAGE

        phoenix-docgen combine --config project.yaml --pdf

    YAML CONFIG STRUCTURE

        # phoenix-docgen combined document configuration
        # Build with: phoenix-docgen combine --config project.yaml --pdf

        cover:
          title_line1: "APPLICATION"
          title_line2: "STRATEGY"
          subtitle: "ACME CORP"
          version: "v1.0 DRAFT"
          author: "JANE SMITH — PRINCIPAL ARCHITECT"
          classification: "[RESTRICTED]"
          year: "2026"

        doc_title: "Application Strategy — Acme Corp"
        output: "Application-Strategy-Combined.html"

        chapters:
          - id: Ch1
            title: "Strategy Overview"
            source: "chapters/01-overview.md"
            version: "v0.2"

          - id: Ch2
            title: "Current State Assessment"
            source: "chapters/02-current-state.md"
            version: "v0.1"

    COVER SECTION

        The cover: object accepts the same fields as single-document
        front-matter (title_line1, title_line2, subtitle, version,
        author, classification, year). See: phoenix-docgen help frontmatter

    CHAPTER FIELDS

        Field             Required  Purpose
        ────────────────  ────────  ─────────────────────────────────
        source            Yes       Path to markdown file (relative
                                    to config file location)
        id                No        Short label on chapter divider
                                    (auto: Ch1, Ch2, ...)
        title             No        Full chapter title (auto: derived
                                    from filename)
        version           No        Chapter version in divider meta
        chapter_num       No        Numeric chapter number (auto:
                                    position in array)
        strip_sections    No        H2 section titles to remove from
                                    this chapter only
        svg_replacements  No        Per-chapter SVG replacement rules

    TOP-LEVEL CONFIG KEYS

        doc_title             Page footer text
        output                Output filename (default: derived from
                              config filename)
        header_pattern        Regex to strip from all chapters
        html_title            Override browser tab title
        front_matter_html     Raw HTML inserted between cover and
                              first chapter (e.g. master TOC)
        footer_extra_lines    Extra lines in document footer
        distribution_notice   Override auto distribution notice

    OPTIONS BLOCK

        The options: object controls advanced processing features
        for multi-chapter documents:

        options:
          renumber_sections: true
          extract_end_matter: true
          build_appendices: true
          prefix_ids: true
          strip_sections:
            - "Internal Notes"
            - "Contact Information"
          chapter_format: "{id}: {title}"
          chapter_subtitle: "Version {version}"

        renumber_sections   (bool, default: false)
            Prefix all H2 and H3 headings with chapter numbers.
            Converts "1. Executive Summary" in Ch3 to "3.1 Executive
            Summary", and H3 sub-headings accordingly (3.1.1, etc.).

        extract_end_matter  (bool, default: false)
            Pull Document Control tables, Next Steps sections, and
            Source References out of each chapter for consolidation.

        build_appendices    (bool, default: false)
            Create consolidated appendices from extracted end matter:
            - Appendix A: Source References (all citations)
            - Appendix B: Next Steps and Open Items
            - Appendix C: Document History (version tables)

        prefix_ids          (bool, default: false)
            Prefix all HTML id attributes with chapter number (e.g.
            id="ch3-section-title") to avoid id collisions between
            chapters. SVG content is preserved untouched.

        strip_sections      (list[string], default: [])
            Remove entire H2 sections by title from all chapters.
            Combines with per-chapter strip_sections.

        chapter_format      (string, default: "{id}: {title}")
            Format string for the chapter divider heading.
            Placeholders: {id}, {title}, {num}

        chapter_subtitle    (string, default: "")
            Format string for the chapter divider subtitle.
            Placeholders: {version}, {num}, {id}, {title}
    """),
)


# ── Topic: cover ─────────────────────────────────────────────────────

TOPIC_COVER = (
    "Cover Page and Branding",
    textwrap.dedent("""\
    phoenix-docgen generates an SVG-based cover page from a template,
    filling in metadata placeholders.

    SVG TEMPLATE

        Location: ~/.local/share/phoenix-docgen/templates/
                  cover-page-template-a4.svg

        The template is an Inkscape SVG (210mm x 297mm / A4) with
        placeholder tokens that are replaced at build time:

        Placeholder         Filled from
        ──────────────────  ──────────────────────────────
        {{TITLE_LINE1}}     title_line1 (uppercased)
        {{TITLE_LINE2}}     title_line2 (uppercased)
        {{SUBTITLE}}        subtitle (uppercased)
        {{AUTHOR}}          author (uppercased)
        {{VERSION}}         version
        {{CLASSIFICATION}}  classification (normalised)
        {{YEAR}}            year

        The template includes gradient backgrounds, the organisation
        logo (embedded as base64 PNG), and theme accent colours.

    LOGO

        The logo is loaded from the active theme's directory
        (configured in theme.yaml under cover → logo).

        Embedded into the SVG cover as a base64-encoded image element,
        positioned according to the theme's logo_position setting.

    DISABLING THE COVER

        Use --no-cover on the CLI or set cover: false in front-matter.
        This omits both the cover page and the blank verso page.

    CLASSIFICATION NORMALISATION

        The classification field accepts flexible input and normalises
        it to a consistent bracketed uppercase format:

        Input                   Output
        ──────────────────────  ─────────────
        RESTRICTED              [RESTRICTED]
        [RESTRICTED]            [RESTRICTED]
        "[RESTRICTED]"          [RESTRICTED]
        restricted              [RESTRICTED]
        Confidential            [CONFIDENTIAL]

        See: phoenix-docgen help classification

    BLANK VERSO

        After the cover, a blank verso page is inserted with the text
        "This page is intentionally blank." This ensures the first
        content page starts on a right-hand (recto) page in duplex
        printing. The verso carries the document title footer and
        classification marker.
    """),
)


# ── Topic: classification ────────────────────────────────────────────

TOPIC_CLASSIFICATION = (
    "Classification Levels and Distribution Notices",
    textwrap.dedent("""\
    phoenix-docgen supports four classification levels, each with an
    auto-generated distribution notice for the document footer.

    CLASSIFICATION LEVELS

        Level           Auto Distribution Notice
        ──────────────  ────────────────────────────────────────
        [RESTRICTED]    Not for distribution outside review team
        [INTERNAL]      For internal use only
        [CONFIDENTIAL]  For designated recipients only
        [PUBLIC]        (no notice)

    WHERE CLASSIFICATION APPEARS

        - Cover page: classification badge
        - Page margins: alternating left/right on every page
        - Info block: classification field
        - Document footer: classification level + distribution notice

    SETTING CLASSIFICATION

        In YAML front-matter:
            classification: "[CONFIDENTIAL]"

        Via CLI override:
            phoenix-docgen build doc.md --classification "[INTERNAL]" --pdf

        Input is normalised (see: phoenix-docgen help cover).

    OVERRIDING THE DISTRIBUTION NOTICE

        The auto-generated notice can be replaced with custom text:

            distribution_notice: "For Board members only — do not copy"

        Set in YAML front-matter (single docs) or top-level config
        (combine mode). An empty string suppresses the notice entirely.
    """),
)


# ── Topic: landscape ─────────────────────────────────────────────────

TOPIC_LANDSCAPE = (
    "Landscape Sections and Table Column Widths",
    textwrap.dedent("""\
    Content can be rendered on landscape (A4 rotated) pages by
    wrapping it in a landscape-section div.

    BASIC USAGE

        <div class="landscape-section">

        ## Wide Tables

        | Col 1 | Col 2 | Col 3 | Col 4 | Col 5 |
        |-------|-------|-------|-------|-------|
        | ...   | ...   | ...   | ...   | ...   |

        </div>

        Everything inside the div renders on landscape pages with
        15mm margins (tighter than portrait's 20mm) for maximum
        content width.

    PAGE BEHAVIOUR

        - Triggers page-break-before: always (new page)
        - Pages use @page landscape rules (A4 landscape, 15mm margins)
        - Page footers (page numbers, classification, doc title)
          continue on landscape pages

    PAGE BREAKS WITHIN LANDSCAPE

        To force page breaks between landscape content (e.g. between
        two appendix tables):

        <div style="page-break-after: always; break-after: page;"></div>

    TABLE COLUMN WIDTHS

        Tables inside .landscape-section use table-layout: fixed, which
        means column widths are enforced by CSS rather than content.

        By default, pandoc generates equal-width columns. phoenix-docgen
        overrides these with specific column width rules in
        shared_styles.py (get_content_css function).

        The current rules target tables by position:

          .landscape-section table:first-of-type
              First table in the landscape section (e.g. risk summary)

          .landscape-section table:nth-of-type(2)
              Second table (e.g. outstanding items tracker)

        Column widths are set on col:nth-child() selectors with
        !important to override pandoc's inline styles. Columns without
        explicit widths split the remaining space equally.

        To customise: edit get_content_css() in shared_styles.py.
        The pattern is:

          .landscape-section table:first-of-type col:nth-child(N) {
              width: X% !important;
          }

    MIXING PORTRAIT AND LANDSCAPE

        Place the landscape div around only the content that needs
        landscape orientation. Content before and after renders in
        portrait as normal. Multiple landscape sections in the same
        document are supported.
    """),
)


# ── Topic: footer ────────────────────────────────────────────────────

TOPIC_FOOTER = (
    "Document Footer Customisation",
    textwrap.dedent("""\
    The document footer appears at the end of the document body.
    Page-margin footers appear on every page.

    DOCUMENT FOOTER

        The document footer includes:
        1. Company name and document title
        2. Classification level
        3. Distribution notice (auto or custom)
        4. Extra lines (if configured)

    PAGE FOOTERS (EVERY PAGE)

        Every page shows three footer elements:
        - Bottom-centre: document title (from doc_title)
        - Bottom-left/right (alternating): page number
        - Bottom-right/left (alternating): classification marker

    doc_title

        Controls the text in the centre of every page footer.

        If not set, derived from title_line1 + title_line2.
        Override in front-matter or combine config:

            doc_title: "Risk Assessment — Building Works — Acme Corp"

    footer_extra_lines

        Adds extra italic lines below the standard footer content.

        In YAML:
            footer_extra_lines:
              - "Distribution: Review team only"
              - "Printed copies are uncontrolled"

    distribution_notice

        Override the auto-generated notice (see: phoenix-docgen help
        classification). Set to empty string to suppress entirely:

            distribution_notice: ""
    """),
)


# ── Topic: branding ──────────────────────────────────────────────────

TOPIC_BRANDING = (
    "Theme System and Branding",
    textwrap.dedent("""\
    phoenix-docgen uses a theme system for branding. Each theme is a
    self-contained directory with colours, fonts, cover template, logo,
    and organisation defaults.

    THEME DIRECTORY STRUCTURE

        themes/mytheme/
          theme.yaml                    # Configuration
          cover-page-template-a4.svg    # SVG cover with {{PLACEHOLDER}} tokens
          logo.png                      # Organisation logo
          fonts/
            LICENCE.txt                 # Font licence
            MyFont-Regular.ttf
            MyFont-Bold.ttf

    THEME SELECTION (priority order)

        1. --theme <name>           CLI flag
        2. theme: <name>            YAML front-matter or combine config
        3. PHOENIX_THEME            Environment variable
        4. default_theme            In ~/.config/phoenix-docgen/config.yaml
        5. Auto-detect              If exactly one theme exists
        6. Built-in defaults        Backward compatible fallback

    THEMES DIRECTORY (where to find themes)

        1. --themes-dir <path>      CLI flag
        2. PHOENIX_THEMES_DIR       Environment variable
        3. themes_dir               In ~/.config/phoenix-docgen/config.yaml
        4. themes/                  Relative to installed scripts

    theme.yaml SCHEMA

        name: "mytheme"
        display_name: "My Organisation"

        organisation:
          name: "MY ORGANISATION LTD"
          short_name: "My Org"
          address: "123 Main Street, Wellington"

        defaults:
          subtitle: "MY ORGANISATION LTD"
          author: "JANE SMITH — PRINCIPAL ARCHITECT"
          classification: "[RESTRICTED]"

        colours:
          primary: "#1a5276"       # Headings, links, TOC
          secondary: "#2c3e50"     # Table headers, chapter dividers
          accent: "#27ae60"        # Blockquote borders, cover swish

        fonts:
          family: "MyFont"
          fallback: "'Segoe UI', Arial, sans-serif"
          weights:
            400: "MyFont-Regular.ttf"
            700: "MyFont-Bold.ttf"

        cover:
          template: "cover-page-template-a4.svg"
          logo: "logo.png"
          logo_position: { x: 85, y: 75, width: 108, height: 108 }

    CREATING A NEW THEME

        1. Copy an existing theme directory
        2. Edit theme.yaml with your organisation's details
        3. Replace the SVG cover template and logo
        4. Add your font files to fonts/
        5. Place in the themes directory

    GLOBAL CONFIGURATION

        ~/.config/phoenix-docgen/config.yaml

        themes_dir: ~/themes/phoenix-docgen
        default_theme: mytheme

    USING SEPARATE REPOS

        Themes are gitignored from the main phoenix-docgen repo.
        Each theme can be its own git repository, cloned into the
        themes directory. For organisational deployment, set themes_dir
        to a shared network path.
    """),
)


# ── Topics registry ──────────────────────────────────────────────────

TOPICS = {
    "frontmatter":    TOPIC_FRONTMATTER,
    "alerts":         TOPIC_ALERTS,
    "markdown":       TOPIC_MARKDOWN,
    "combine":        TOPIC_COMBINE,
    "cover":          TOPIC_COVER,
    "classification": TOPIC_CLASSIFICATION,
    "landscape":      TOPIC_LANDSCAPE,
    "footer":         TOPIC_FOOTER,
    "branding":       TOPIC_BRANDING,
}


# ── Public API ───────────────────────────────────────────────────────

def show_help(topic=None):
    """Print help for a specific topic, or the topic listing."""
    if topic is None:
        print(OVERVIEW)
        return

    key = topic.lower().replace("-", "_")
    if key not in TOPICS:
        print(f"\n  Unknown help topic: '{topic}'")
        print()
        print("  Available topics:")
        for k, (title, _) in TOPICS.items():
            print(f"    {k:<18s}{title}")
        print()
        print(f"  Run 'phoenix-docgen help' for the full topic listing.")
        print()
        return

    title, body = TOPICS[key]
    header = f"phoenix-docgen help — {title}"
    print()
    print(header)
    print("─" * len(header))
    print()
    print(body)
