# Multi-Chapter Documents (`combine`)

The `combine` command assembles multiple markdown files into a single branded
document with chapter dividers, a shared cover page, and optional consolidated
appendices. Use it when you need to publish several related documents —
strategies, assessments, project plans — as one cohesive PDF.

## When to Use Combine

| Scenario | Command |
|----------|---------|
| Single markdown file | `pdg build report.md --pdf` |
| Multiple files into one document | `pdg combine --config project.yaml --pdf` |

Choose `combine` when:

- Your content is naturally split across several files (one per chapter or
  workstream).
- You want a single cover page and unified page numbering across all chapters.
- You need consolidated appendices that pull references, next steps, and
  version history from every chapter into one place.
- Different chapters have independent version numbers or authors.

## Usage

```
pdg combine --config project.yaml --pdf
```

| Flag | Purpose |
|------|---------|
| `--config FILE` | Path to the YAML configuration file (required) |
| `--pdf` | Render the final document to PDF via WeasyPrint |
| `--html` | Keep the intermediate HTML output |
| `--output FILE` | Override the output file path |
| `--theme NAME` | Override the theme (can also be set in config) |
| `--themes-dir PATH` | Override the themes directory |

If neither `--pdf` nor `--html` is given, only HTML is produced.  When `--pdf`
is given without `--html`, the intermediate HTML is removed after rendering.

---

## YAML Configuration Structure

The config file drives everything.  Below is a fully annotated example
covering every available field.

```yaml
# ── phoenix-docgen combined document configuration ──────────────────
# Build with: pdg combine --config project.yaml --pdf
# Reference:  pdg help combine

# ── Cover page metadata ────────────────────────────────────────────
# Accepts the same fields as single-document front-matter.
cover:
  title_line1: "ANNUAL"                 # Line 1 of cover title (uppercased)
  title_line2: "STRATEGY"               # Line 2 of cover title (uppercased)
  subtitle: "ACME CONSULTING LTD"       # Organisation line below title (uppercased)
  version: "v1.0 DRAFT"                 # Version badge on cover
  author: "J. SMITH — LEAD ANALYST"     # Author line on cover (uppercased)
  classification: "[RESTRICTED]"        # Classification badge and page markers
  year: "2026"                          # Year badge on cover

# ── Document-level settings ────────────────────────────────────────
doc_title: "Annual Strategy — Acme Consulting"  # Text in the centre of every page footer
output: "Annual-Strategy-Combined.html"         # Output filename (default: derived from config filename)

# theme: mytheme                          # Override the active theme by name
# html_title: "Strategy 2026"             # Override the browser <title> element
# header_pattern: "^Auto-Header.*"        # Regex to strip a pandoc-generated header from all chapters
# distribution_notice: "Board only"       # Override the auto-generated distribution notice
# footer_extra_lines:                     # Extra italic lines in the document footer
#   - "Printed copies are uncontrolled"
#   - "Review period ends 31 March 2026"

# ── Front matter (optional) ───────────────────────────────────────
# Raw HTML inserted between the cover/verso and the first chapter.
# Use this for a master table of contents, a preface, or legal text.
#
# front_matter_html: |
#   <div class="master-toc">
#     <h2>Contents</h2>
#     <p>Ch1: Overview .............. 3</p>
#     <p>Ch2: Current State ........ 12</p>
#     <p>Ch3: Roadmap .............. 25</p>
#   </div>

# ── Chapters ──────────────────────────────────────────────────────
chapters:
  - source: "chapters/01-overview.md"       # Path relative to this config file (REQUIRED)
    id: "Ch1"                               # Short label on the chapter divider (default: Ch1, Ch2, ...)
    title: "Strategy Overview"              # Full chapter title (default: derived from filename)
    version: "v0.3"                         # Per-chapter version shown in divider meta line
    # chapter_num: 1                        # Numeric chapter number (default: position in array)
    # strip_sections:                       # H2 section titles to remove from THIS chapter only
    #   - "Internal Notes"
    # svg_replacements:                     # Per-chapter SVG replacement rules
    #   - ascii_pattern: '<pre><code>.*?diagram.*?</code></pre>'
    #     svg_file: "diagrams/ch1-overview.svg"

  - source: "chapters/02-current-state.md"
    id: "Ch2"
    title: "Current State Assessment"
    version: "v0.2"

  - source: "chapters/03-roadmap.md"
    id: "Ch3"
    title: "Implementation Roadmap"
    version: "v0.1"

# ── Processing options ────────────────────────────────────────────
options:
  renumber_sections: true                   # Prefix H2/H3 with chapter numbers
  extract_end_matter: true                  # Pull out Document Control, Next Steps, References
  build_appendices: true                    # Create consolidated Appendices A, B, C
  prefix_ids: true                          # Add chapter prefix to HTML id attributes
  strip_sections:                           # Remove named H2 sections from ALL chapters
    - "Internal Notes"
    - "Contact Information"
  chapter_format: "{id}: {title}"           # Chapter divider heading format
  chapter_subtitle: "Version {version}"     # Chapter divider subtitle format
```

---

## Cover Section

The `cover` object accepts the same fields as the single-document YAML
front-matter.  All values are optional; anything not specified falls back to
the theme defaults and then to the built-in defaults.

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `title_line1` | string | `"DOCUMENT"` | Uppercased on the cover page |
| `title_line2` | string | `"TITLE"` | Uppercased on the cover page |
| `subtitle` | string | From theme | Organisation name (uppercased) |
| `version` | string | `"v0.1 DRAFT"` | Version badge on the cover |
| `author` | string | From theme | Author line (uppercased on cover) |
| `classification` | string | `"[RESTRICTED]"` | Normalised to `[UPPERCASE]` format |
| `year` | string | Current year | Year badge on the cover |

See `pdg help frontmatter` for full details on each field.

---

## Chapters Array

Each entry in the `chapters` list represents one markdown file that becomes a
chapter in the combined document.

### Chapter Fields

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `source` | Yes | -- | Path to the markdown file, **relative to the config file location** |
| `id` | No | `Ch1`, `Ch2`, ... | Short label shown on the chapter divider page |
| `title` | No | Derived from filename | Full chapter title on the divider page |
| `version` | No | (none) | Per-chapter version shown in the divider meta line |
| `chapter_num` | No | Position in array | Numeric chapter number used for section renumbering and id prefixing |
| `strip_sections` | No | `[]` | List of H2 titles to remove from **this chapter only** (combined with global `strip_sections`) |
| `svg_replacements` | No | `[]` | Per-chapter SVG replacement rules (same format as single-document `svg_replacements`) |

### How Chapters Are Processed

For each chapter, the pipeline runs these steps in order:

1. Convert markdown to HTML via pandoc (no TOC per chapter).
2. Apply per-chapter SVG replacements.
3. Strip the H1 heading (the chapter divider replaces it).
4. Strip `header_pattern` matches (if configured).
5. Strip sections by title (per-chapter list merged with global list).
6. Process GitHub-style alerts into styled callout boxes.
7. Compact duplicate footnotes.
8. Extract end matter (if `extract_end_matter` is enabled).
9. Renumber H2/H3 headings with chapter prefix (if `renumber_sections` is enabled).
10. Prefix HTML `id` attributes (if `prefix_ids` is enabled).

---

## Top-Level Configuration Keys

These keys sit at the root of the YAML config, alongside `cover` and
`chapters`.

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `doc_title` | string | Derived from cover title lines | Text shown in the centre of every page footer |
| `output` | string | `<config-stem>-Combined.html` | Output filename |
| `theme` | string | Auto-detected | Override the active theme by name |
| `header_pattern` | string | (none) | Regex to strip from all chapters (matches H2 through first HR) |
| `html_title` | string | Same as `doc_title` | Override the HTML `<title>` element (browser tab text) |
| `front_matter_html` | string | (none) | Raw HTML inserted between the cover verso and the first chapter |
| `footer_extra_lines` | list | `[]` | Extra italic lines appended to the document footer |
| `distribution_notice` | string | Auto from classification | Override the auto-generated distribution notice text |

---

## Options Block

The `options` object controls advanced processing features that apply
across all chapters.  Every option defaults to `false` or empty.

```yaml
options:
  renumber_sections: true
  extract_end_matter: true
  build_appendices: true
  prefix_ids: true
  strip_sections:
    - "Internal Notes"
  chapter_format: "{id}: {title}"
  chapter_subtitle: "Version {version}"
```

### `renumber_sections` (boolean, default: `false`)

Prefixes all H2 and H3 headings with chapter-scoped numbers.

Existing numbered headings are remapped:

| Original (in Chapter 3 source) | Renumbered Output |
|-------------------------------|-------------------|
| `## 1. Executive Summary` | `## 3.1 Executive Summary` |
| `## 4A. Licence Data` | `## 3.N Licence Data` |
| `## Appendix A: Glossary` | `## 3.N Glossary` |
| `### 1.2 Sub-Heading` | `### 3.1.2 Sub-Heading` |

H3 sub-headings are renumbered relative to their parent H2 section.  Headings
that do not match a recognised numbering pattern (e.g. a plain `## Summary`)
are left unchanged.

### `extract_end_matter` (boolean, default: `false`)

Pulls three types of trailing content out of each chapter's body for later
consolidation:

- **Document Control** -- the version-history table that follows a
  `**Document Control**` bold paragraph.
- **Next Steps** -- list items following a `**Next Steps:**` bold label.
- **Source References** -- content inside a `<div class="section-references">`
  wrapper.

The extracted content is removed from the chapter body.  If
`build_appendices` is also enabled, the extracted content is assembled into
consolidated appendices at the end of the document.

### `build_appendices` (boolean, default: `false`)

Requires `extract_end_matter: true`.  Creates three consolidated appendix
sections from the extracted end matter:

| Appendix | Contents |
|----------|----------|
| **Appendix A: Source References** | All source citations, grouped by chapter |
| **Appendix B: Next Steps and Open Items** | All next-steps lists and notes, grouped by chapter |
| **Appendix C: Document History** | All Document Control version tables, grouped by chapter |

Each appendix begins with a full-page divider (matching the chapter divider
style) and organises content under `### Chapter N: Title` sub-headings.

If a chapter has no content for a given appendix, it is simply omitted from
that section.  If no chapters contribute any content, the appendix displays a
placeholder message.

### `prefix_ids` (boolean, default: `false`)

Adds a chapter-number prefix to all HTML `id` attributes within each
chapter's body.  For example, an element with `id="executive-summary"` in
Chapter 3 becomes `id="ch3-executive-summary"`.

This prevents id collisions when multiple chapters use the same heading text
(e.g. every chapter has an "## Overview" section).

SVG content is preserved untouched -- SVGs use internal `id` references
(`url(#id)`, `xlink:href`) that would break if prefixed.  The tool
temporarily replaces SVG blocks with placeholders, prefixes all other ids,
then restores the SVG blocks.

### `strip_sections` (list of strings, default: `[]`)

A list of H2 section titles to remove from **all** chapters.  Each matching
H2 and everything up to the next H2 (or end of chapter) is removed.

This is combined with per-chapter `strip_sections` lists, so you can strip
some sections globally and others from individual chapters.

```yaml
options:
  strip_sections:
    - "Internal Notes"       # removed from every chapter
    - "Contact Information"  # removed from every chapter

chapters:
  - source: "overview.md"
    strip_sections:
      - "Draft Comments"     # removed from this chapter only
```

### `chapter_format` (string, default: `"{id}: {title}"`)

Format string for the heading on each chapter divider page.  Available
placeholders:

| Placeholder | Value |
|-------------|-------|
| `{id}` | Chapter id (e.g. `Ch1`) |
| `{title}` | Chapter title (e.g. `Strategy Overview`) |
| `{num}` | Numeric chapter number (e.g. `1`) |

Examples:

```yaml
chapter_format: "{id}: {title}"         # "Ch1: Strategy Overview"
chapter_format: "Chapter {num} — {title}"  # "Chapter 1 — Strategy Overview"
chapter_format: "{title}"               # "Strategy Overview"
```

### `chapter_subtitle` (string, default: `""`)

Format string for the subtitle line beneath the heading on each chapter
divider page.  Available placeholders:

| Placeholder | Value |
|-------------|-------|
| `{version}` | Chapter version (e.g. `v0.3`) |
| `{num}` | Numeric chapter number |
| `{id}` | Chapter id |
| `{title}` | Chapter title |

If left empty (the default), no subtitle is shown.

```yaml
chapter_subtitle: "Version {version}"               # "Version v0.3"
chapter_subtitle: "{id} — Version {version}"         # "Ch1 — Version v0.3"
```

---

## Output Structure

The final combined document is assembled in this order:

```
1. Cover page               Full-page SVG cover with title, version, classification
2. Blank verso              "This page is intentionally blank." (for duplex printing)
3. Front matter HTML        Optional custom HTML (e.g. master table of contents)
4. For each chapter:
   a. Chapter divider       Full-page coloured divider with title, subtitle, meta line
   b. Chapter body          Converted markdown content (alerts, footnotes, tables, etc.)
5. Appendices (optional)
   a. Appendix A divider    Source References
   b. Appendix A body
   c. Appendix B divider    Next Steps and Open Items
   d. Appendix B body
   e. Appendix C divider    Document History
   f. Appendix C body
6. Document footer          Organisation name, classification, distribution notice
```

Every page carries:

- **Bottom centre:** document title (from `doc_title`)
- **Bottom left/right (alternating):** page number
- **Bottom right/left (alternating):** classification marker

---

## Worked Example: Three-Chapter Strategy Report

Suppose you have three markdown files in a `chapters/` directory:

```
project/
  project.yaml
  chapters/
    01-overview.md
    02-analysis.md
    03-recommendations.md
```

### Chapter files

Each chapter file is a standard markdown document with headings, tables, and
a Document Control block at the end:

```markdown
# Strategy Overview

## 1. Executive Summary

This chapter outlines the overall strategic direction...

## 2. Background

The organisation has operated under the current model since 2019...

---

**Document Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | January 2026 | J. Smith | Initial draft |
| 0.2 | February 2026 | J. Smith | Added stakeholder input |

**Next Steps:**

- Circulate to the leadership team for review
- Schedule board presentation for March
```

### Configuration

```yaml
cover:
  title_line1: "ANNUAL"
  title_line2: "STRATEGY"
  subtitle: "ACME CONSULTING LTD"
  version: "v1.0 DRAFT"
  author: "J. SMITH — LEAD ANALYST"
  classification: "[RESTRICTED]"
  year: "2026"

doc_title: "Annual Strategy — Acme Consulting"
output: "Annual-Strategy-Combined.html"

chapters:
  - source: "chapters/01-overview.md"
    id: "Ch1"
    title: "Strategy Overview"
    version: "v0.3"

  - source: "chapters/02-analysis.md"
    id: "Ch2"
    title: "Current State Analysis"
    version: "v0.2"

  - source: "chapters/03-recommendations.md"
    id: "Ch3"
    title: "Recommendations and Roadmap"
    version: "v0.1"
    strip_sections:
      - "Draft Comments"

options:
  renumber_sections: true
  extract_end_matter: true
  build_appendices: true
  prefix_ids: true
  chapter_format: "{id}: {title}"
  chapter_subtitle: "Version {version}"
```

### Build

```
pdg combine --config project.yaml --pdf
```

### What happens

1. The cover page is generated with "ANNUAL STRATEGY" as the title, the
   classification badge, and the version number.
2. A blank verso page follows for duplex printing.
3. Each chapter gets a full-page coloured divider showing, for example,
   "Ch1: Strategy Overview" with "Version v0.3" beneath it and a meta line
   reading "Version v0.3 (Draft) . March 2026 . Classification: RESTRICTED".
4. The chapter body follows with renumbered headings (e.g. the original
   "1. Executive Summary" in Chapter 3 becomes "3.1 Executive Summary").
5. Document Control tables, Next Steps, and References are extracted from
   each chapter.
6. Three appendices are generated at the end:
   - **Appendix A** consolidates all source references.
   - **Appendix B** consolidates all next-steps lists.
   - **Appendix C** consolidates all version-history tables.
7. The document footer shows the organisation name, classification level,
   and distribution notice.
8. The result is written to `Annual-Strategy-Combined.pdf`.

---

## Tips

- **Chapter source paths** are always relative to the config file location,
  not the working directory.  This means you can run the build from anywhere.
- **Scaffolding:** use `pdg init --config project.yaml --chapters ch1.md ch2.md`
  to generate a starter config with chapter entries pre-filled.
- **HTML preview:** omit `--pdf` to get just the HTML file, which you can open
  in a browser to check layout before committing to a PDF render.
- **Per-chapter versions** appear in the chapter divider meta line and in
  Appendix C.  Update them independently as each chapter progresses through
  review.
- **Global strip_sections** is useful for removing boilerplate sections
  (e.g. "Contact Information") that exist in standalone versions of each
  chapter but are not needed in the combined document.
