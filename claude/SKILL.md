---
name: phoenix-docgen
description: Build branded PDF documents from markdown using configurable themes. Use when creating, scaffolding, or building documents, reports, or deliverables. Handles single documents (from YAML front-matter) and multi-chapter combined documents (from YAML config files). Triggers include document generation, PDF creation, report building, branded output, or when the user says "phoenix-docgen", "build a document", "generate a PDF", or "create a report".
---

# phoenix-docgen — Branded Document Builder

Converts markdown documents to professionally styled HTML and PDF with configurable themes (fonts, colours, cover page, logo, organisation details).

## Tool Location

```
Command:         phoenix-docgen                          (on PATH via ~/.local/bin/)
Shell wrapper:   ~/.local/bin/phoenix-docgen
Python backend:  ~/.local/share/phoenix-docgen/phoenix-docgen.py
Help topics:     ~/.local/share/phoenix-docgen/help_topics.py
Theme system:    ~/.local/share/phoenix-docgen/theme.py
Themes:          ~/.local/share/phoenix-docgen/themes/    (symlinked from repo)
Global config:   ~/.config/phoenix-docgen/config.yaml
Venv:            ~/.local/share/phoenix-docgen/venv/
```

**Invoke directly as `phoenix-docgen`** — it's on PATH. The wrapper handles venv activation automatically.

---

## Commands

### `help` — Comprehensive Documentation

Topic-based help system with detailed reference for all features.

```bash
# List all help topics
phoenix-docgen help

# View a specific topic
phoenix-docgen help frontmatter    # YAML front-matter fields and defaults
phoenix-docgen help alerts         # GitHub-style alert boxes and inline glyphs
phoenix-docgen help markdown       # Authoring features (landscape, page breaks, footnotes)
phoenix-docgen help combine        # Multi-chapter YAML config and options
phoenix-docgen help cover          # Cover page, SVG template, logo
phoenix-docgen help classification # Classification levels and distribution notices
phoenix-docgen help landscape      # Landscape sections and table column widths
phoenix-docgen help footer         # Document footer customisation
phoenix-docgen help branding       # Theme system, creating themes, branding config
```

### `init` — Scaffold a New Document

Creates a richly commented markdown file with YAML front-matter, or a YAML config for multi-chapter documents. Scaffolds include inline hints for all available features.

```bash
# Single document with defaults
phoenix-docgen init report.md

# Single document with pre-filled metadata and a specific theme
phoenix-docgen init report.md \
  --title1 "APPLICATION" --title2 "STRATEGY" \
  --subtitle "FRAMEWORK v2.0" --doc-type "Strategy Framework" \
  --theme mytheme

# Multi-chapter YAML config
phoenix-docgen init --config project.yaml

# Multi-chapter with chapter list pre-filled
phoenix-docgen init --config project.yaml \
  --chapters intro.md analysis.md recommendations.md
```

### `build` — Build a Single Document

Converts markdown (with YAML front-matter) to branded HTML and optionally PDF.

```bash
# HTML only
phoenix-docgen build report.md

# HTML + PDF
phoenix-docgen build report.md --pdf

# With a specific theme
phoenix-docgen build report.md --theme mytheme --pdf

# With CLI overrides (override any front-matter value)
phoenix-docgen build report.md \
  --version "v2.0 FINAL" --pdf

# Without cover page or info block
phoenix-docgen build report.md \
  --no-cover --no-info-block --pdf
```

**Build options:**
- `--pdf` — also generate PDF via WeasyPrint
- `--html` — keep HTML output (default if `--pdf` not given; add alongside `--pdf` to keep both)
- `--output PATH` — override output file path
- `--theme NAME` — use a specific theme (overrides front-matter and config)
- `--themes-dir PATH` — override themes directory location
- `--no-toc` — disable table of contents
- `--no-info-block` — disable metadata info block after cover
- `--no-cover` — disable cover page entirely
- `--header-pattern REGEX` — strip matching H2-through-HR block from pandoc output

### `combine` — Build Multi-Chapter Document

Combines multiple markdown files into a single document with chapter dividers, driven by a YAML config.

```bash
phoenix-docgen combine \
  --config project.yaml --pdf

# With theme override
phoenix-docgen combine \
  --config project.yaml --theme mytheme --pdf
```

---

## Theme System

phoenix-docgen uses a theme system for branding. Each theme is a self-contained directory with a `theme.yaml` configuration file plus assets (SVG template, logo, fonts).

### Theme Structure

```
themes/mytheme/
  theme.yaml                    # Configuration
  cover-page-template-a4.svg    # SVG cover with {{PLACEHOLDER}} tokens
  logo.png                      # Organisation logo
  fonts/
    LICENCE.txt                 # Font licence
    MyFont-Regular.ttf
    MyFont-Bold.ttf
```

### Theme Selection (priority order, highest wins)

1. `--theme <name>` CLI flag
2. `theme: <name>` in YAML front-matter or combine config
3. `PHOENIX_THEME` environment variable
4. `default_theme` in `~/.config/phoenix-docgen/config.yaml`
5. Auto-detect (if exactly one theme exists in the themes directory)
6. No theme: fall back to built-in defaults (backward compatible)

### Themes Directory Discovery (priority order, highest wins)

1. `--themes-dir <path>` CLI flag
2. `PHOENIX_THEMES_DIR` environment variable
3. `themes_dir` in `~/.config/phoenix-docgen/config.yaml`
4. `themes/` relative to installed scripts (default)

### Global Configuration

Location: `~/.config/phoenix-docgen/config.yaml`

```yaml
themes_dir: ~/themes/phoenix-docgen
default_theme: mytheme
```

Override config file location with `PHOENIX_CONFIG` environment variable.

### theme.yaml Schema

```yaml
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
  primary: "#1a5276"        # Headings, links, TOC, footnote refs
  secondary: "#2c3e50"      # Table headers, chapter dividers, footer border
  accent: "#27ae60"         # Blockquote border, cover swish gradient

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
```

### Creating a New Theme

1. Copy an existing theme directory as a starting point
2. Edit `theme.yaml` with your organisation's details, colours, and fonts
3. Replace the SVG cover template and logo
4. Place the theme directory in your themes directory

### Using Separate Repos for Themes

Themes are gitignored from the main repo. Each theme can be its own git repository:

```bash
cd ~/Development/phoenix-docgen/themes
git clone <theme-repo-url> mytheme
```

For organisational deployment, set `themes_dir` in the global config to a shared network path.

---

## Metadata Priority

When building, metadata is merged from multiple sources (highest priority wins):

1. **CLI arguments** (`--version`, `--title1`, etc.)
2. **YAML front-matter** in the markdown file
3. **YAML config file** (for `combine` mode)
4. **Theme defaults** (`defaults:` in `theme.yaml`)
5. **Built-in defaults** (current year, A4, Restricted)

---

## YAML Front-Matter Format (Single Documents)

Place at the top of any markdown file between `---` markers:

```yaml
---
title_line1: APPLICATION        # Cover page title line 1 (UPPERCASE)
title_line2: STRATEGY           # Cover page title line 2 (UPPERCASE)
subtitle: FRAMEWORK v2.0       # Cover page subtitle
version: v2.0 DRAFT            # Version shown on cover and info block
doc_type: Strategy Framework    # Document type in info block
classification: "[RESTRICTED]" # Classification marker
author: DANIEL HOPKIRK — TECH LEAD / ARCHITECT
year: "2026"
theme: mytheme                  # Theme to use (optional, overridden by --theme)
toc: true                       # Generate table of contents (default: true)
toc_depth: 3                    # TOC heading depth (default: 3)
info_block: true                # Show metadata block after cover (default: true)
cover: true                     # Show cover page (default: true)
# Optional:
doc_title: "Custom Footer Title"  # Override the page footer text
doc_id: "A1"                      # Document ID prefix
# distribution_notice: "Custom"   # Override auto distribution notice
# footer_extra_lines:              # Extra lines in document footer
#   - "Distribution: Review team only"
# header_pattern: 'regex here'    # Strip matching pattern from pandoc output
---
```

**All fields are optional.** Unspecified fields use theme defaults (if a theme is active) or built-in defaults.

**Field reference:**

| Field | Default | Purpose |
|-------|---------|---------|
| `title_line1` | DOCUMENT | First line of cover title (uppercase) |
| `title_line2` | TITLE | Second line of cover title (uppercase) |
| `subtitle` | (from theme) | Cover subtitle |
| `version` | v0.1 DRAFT | Version on cover and info block |
| `doc_type` | Report | Document type in info block |
| `classification` | (from theme) | Classification marker (see Classification section) |
| `author` | (from theme) | Author line |
| `year` | (current year) | Year on cover badge |
| `theme` | (from config/CLI) | Theme name to use |
| `toc` | true | Generate table of contents |
| `toc_depth` | 3 | TOC heading depth (1-6) |
| `info_block` | true | Show metadata info block after cover |
| `cover` | true | Show cover page and blank verso |
| `doc_title` | (derived from title) | Page footer text |
| `doc_id` | (none) | Document ID prefix (e.g. A1, Ch1) |
| `header_pattern` | (none) | Regex to strip from pandoc output |
| `distribution_notice` | (auto from classification) | Override distribution notice text |
| `footer_extra_lines` | [] | Extra italic lines in document footer |
| `svg_replacements` | [] | ASCII art to SVG replacement rules |

---

## YAML Config Format (Multi-Chapter Documents)

```yaml
# project-config.yaml
theme: mytheme                  # Theme to use (optional)

cover:
  title_line1: CRM PLATFORM
  title_line2: STRATEGIC REVIEW
  subtitle: "PHASE 1 — INTERMEDIATE REVIEW"
  version: "v2.0 DRAFT"
  author: DANIEL HOPKIRK — TECH LEAD / ARCHITECT
  classification: "[RESTRICTED]"
  year: "2026"

doc_title: "CRM Platform Strategic Review — Phase 1"

# Optional: custom HTML rendered between cover and first chapter
front_matter_html: |
  <div class="master-toc">
    <h1>Document Title</h1>
    <p>Introduction text...</p>
  </div>

chapters:
  - id: A1
    title: Current State Architecture Overview
    source: A1-Current-State-Architecture-Overview.md
    version: "v0.4"
  - id: A2
    title: Architecture Principles Assessment
    source: A2-Architecture-Principles-Assessment.md
    version: "v0.1"

header_pattern: 'CRM\s+Platform\s+Strategic\s+Review\s+2025'
output: Phase1-Combined.html
```

**Chapter fields:**

| Field | Required | Purpose |
|-------|----------|---------|
| `source` | **Yes** | Path to markdown file (relative to config file) |
| `id` | No (auto: Ch1, Ch2...) | Short identifier on chapter divider |
| `title` | No (derived from filename) | Full chapter title |
| `version` | No | Chapter-specific version in divider meta |
| `chapter_num` | No (auto: position) | Numeric chapter number |
| `strip_sections` | No | H2 titles to remove from this chapter |
| `svg_replacements` | No | Per-chapter SVG replacement rules |

---

## Advanced Combine Options

The `options:` block in combine YAML configs controls processing features:

```yaml
options:
  renumber_sections: true       # Prefix H2/H3 with chapter numbers (3.1, 3.1.1)
  extract_end_matter: true      # Pull out Document Control, Next Steps, References
  build_appendices: true        # Create consolidated Appendices A, B, C
  prefix_ids: true              # Prefix HTML ids to avoid collisions
  strip_sections:               # Remove named H2 sections from all chapters
    - "Internal Notes"
  chapter_format: "{id}: {title}"    # Chapter divider heading format
  chapter_subtitle: "Version {version}"  # Divider subtitle format
```

| Option | Default | Purpose |
|--------|---------|---------|
| `renumber_sections` | false | Prefix H2/H3 with chapter numbers (e.g. "1. Summary" in Ch3 -> "3.1 Summary") |
| `extract_end_matter` | false | Extract Document Control, Next Steps, References for consolidation |
| `build_appendices` | false | Create Appendix A (references), B (next steps), C (document history) |
| `prefix_ids` | false | Prefix HTML ids with chapter number to avoid collisions |
| `strip_sections` | [] | Remove H2 sections by title from all chapters |
| `chapter_format` | `{id}: {title}` | Format for chapter divider heading ({id}, {title}, {num}) |
| `chapter_subtitle` | (empty) | Format for divider subtitle ({version}, {num}, {id}, {title}) |

**Top-level config keys:**

| Key | Purpose |
|-----|---------|
| `theme` | Theme name to use for this document |
| `front_matter_html` | Raw HTML between cover and first chapter (master TOC, etc.) |
| `footer_extra_lines` | Extra italic lines in document footer |
| `distribution_notice` | Override auto distribution notice |
| `html_title` | Override browser tab title |

---

## Markdown Authoring Features

### Alerts (GitHub-Style Callout Boxes)

Five alert types with coloured borders and icons:

```markdown
> [!NOTE]
> Informational content.

> [!TIP]
> A helpful suggestion.

> [!IMPORTANT]
> Critical information.

> [!WARNING]
> Potential issue.

> [!CAUTION]
> Dangerous action.
```

**Inline glyphs** — small coloured icons inline in text:
```markdown
This action [!WARNING] may cause data loss.
```

### Landscape Sections

Wrap content in a landscape div for A4 landscape pages (15mm margins):

```html
<div class="landscape-section">

## Wide Tables

| Col 1 | Col 2 | Col 3 | Col 4 | Col 5 |
|-------|-------|-------|-------|-------|
| ...   | ...   | ...   | ...   | ...   |

</div>
```

Tables inside landscape sections use `table-layout: fixed` with customisable column widths. Column width rules are in `shared_styles.py` -> `get_content_css()`.

### Page Breaks

Force a page break between sections:

```html
<div style="page-break-after: always; break-after: page;"></div>
```

### Footnotes

Standard pandoc footnote syntax with automatic duplicate compaction:

```markdown
This claim needs a source[^1]. Another reference[^2].

[^1]: Smith, J. (2025). Example Reference.
[^2]: Smith, J. (2025). Example Reference.
```

Duplicate footnotes with identical text are compacted into combined entries showing all reference numbers (e.g. `[1][2] Smith, J. ...`).

### Raw HTML

Any HTML passes through pandoc. Common uses: landscape divs, page breaks, SVG diagrams, custom styling.

---

## Classification and Distribution Notices

Four classification levels, each with an auto-generated distribution notice:

| Level | Distribution Notice |
|-------|---------------------|
| `[RESTRICTED]` | Not for distribution outside review team |
| `[INTERNAL]` | For internal use only |
| `[CONFIDENTIAL]` | For designated recipients only |
| `[PUBLIC]` | (no notice) |

Classification appears on: cover page, every page footer (alternating), info block, document footer.

Input is normalised — `RESTRICTED`, `[RESTRICTED]`, `"[RESTRICTED]"`, `restricted` all become `[RESTRICTED]`.

Override the auto notice: `distribution_notice: "Custom text"` in front-matter or config.

---

## Footer Customisation

- **`doc_title`** — centre page footer text (derived from title if not set)
- **`footer_extra_lines`** — extra italic lines in the document footer
- **`distribution_notice`** — override auto distribution notice (empty string suppresses)

---

## Output Structure

### Single Document

```
+-------------------------+
| SVG Cover Page          |  <- Theme template with title, version, logo
| (title, subtitle,       |
|  version, author, year) |
+-------------------------+
| Blank Verso             |  <- "This page is intentionally blank"
+-------------------------+
| Info Block              |  <- Document type, classification, version, date
| Table of Contents       |  <- Pandoc-generated from headings
| Document Body           |  <- Markdown content converted to styled HTML
| Document Footer         |  <- Organisation name, classification
+-------------------------+
```

### Multi-Chapter Document

```
+-------------------------+
| SVG Cover Page          |
+-------------------------+
| Blank Verso             |
+-------------------------+
| Front Matter HTML       |  <- Optional intro/TOC from config
+-------------------------+
| Chapter Divider (Ch 1)  |  <- Full-page divider with title
| Chapter 1 Body          |
+-------------------------+
| Chapter Divider (Ch 2)  |
| Chapter 2 Body          |
+-------------------------+
| ...                     |
+-------------------------+
| Document Footer         |
+-------------------------+
```

---

## Brand Styling (Theme-Driven)

All output uses the active theme's brand standards. Typical theme provides:

- **Font**: Custom font family (Regular + Bold weights) — embedded as base64
- **Colours**: Primary, secondary, and accent colours from theme.yaml
- **Page**: A4 portrait (20mm margins), landscape available via wrapper div (15mm margins)
- **Cover**: SVG template with logo, accent swish, `{{PLACEHOLDER}}` tokens
- **Page footers**: Document title centred, page numbers, classification marker (alternating L/R)
- **Chapter dividers**: Dark full-page with white text (uses `secondary` colour)
- **Tables**: Dark header (uses `secondary` colour), alternating row striping, landscape tables use fixed layout
- **Alerts**: 5 types with coloured borders and SVG icons (note, tip, important, warning, caution)

When no theme is active, built-in defaults provide backward-compatible output.

---

## Module Architecture

The following modules power the styling (in `~/.local/share/phoenix-docgen/`):

- **`theme.py`** — Theme class, global config loader, theme resolver
- **`shared_styles.py`** — CSS generation: typography, tables, print layout, @page rules, landscape sections, alerts, chapter dividers (all theme-aware)
- **`help_topics.py`** — Topic-based help system content and dispatcher
- **`cover_utils.py`** — SVG cover page template filling + logo embedding (theme-aware)

---

## Workflow Examples

### Create a New Strategy Document

```bash
# 1. Scaffold (generates commented template with hints)
phoenix-docgen init \
  "/path/to/AI-Strategy.md" \
  --title1 "AI" --title2 "STRATEGY" \
  --subtitle "TECHNOLOGY STRATEGY 2026" \
  --doc-type "Strategy Document" \
  --theme mytheme

# 2. Edit the markdown content

# 3. Build
phoenix-docgen build "/path/to/AI-Strategy.md" --pdf
```

### Build an Existing Document with New Version

```bash
phoenix-docgen build document.md --version "v3.0 FINAL" --pdf
```

### Create a Multi-Chapter Report

```bash
# 1. Scaffold config (generates commented YAML with all options)
phoenix-docgen init \
  --config report-config.yaml \
  --chapters chapter1.md chapter2.md chapter3.md

# 2. Edit the YAML config

# 3. Build
phoenix-docgen combine --config report-config.yaml --pdf
```

---

## Dependencies

The tool requires:
- **pandoc** — markdown to HTML conversion (system install)
- **WeasyPrint** — HTML to PDF rendering (in venv)
- **pyyaml** — YAML parsing (in venv)

All Python dependencies are in the venv at:
`~/.local/share/phoenix-docgen/venv/`

The shell wrapper activates this venv automatically.

---

## Troubleshooting

### "pandoc: command not found"
Install pandoc: `brew install pandoc`

### "weasyprint not installed"
```bash
cd ~/.local/share/phoenix-docgen
source venv/bin/activate && pip install weasyprint pyyaml
```

### Cover page version not showing
Ensure the `version` field is set in YAML front-matter or passed via `--version`.

### Output goes to wrong directory
Use `--output /absolute/path/to/output.html` to control output location.

### Existing file won't be overwritten by init
`init` refuses to overwrite existing files. Delete the target first or choose a new name.

### Landscape tables not filling width
Tables in `.landscape-section` use `table-layout: fixed`. Column widths are controlled via `col:nth-child()` selectors in `shared_styles.py` -> `get_content_css()`. Pandoc's equal-width colgroup inline styles are overridden with `!important`.

### Theme not found
Check that the theme directory exists in one of the searched locations. Run `phoenix-docgen help branding` for the full resolution order.
