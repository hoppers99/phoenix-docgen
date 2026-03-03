# phoenix-docgen

phoenix-docgen (`pdg`) converts Markdown documents to professionally styled HTML and PDF output using configurable themes. It handles everything from single-page reports to multi-chapter combined documents, with full control over branding, layout, and classification.

## Feature Highlights

- **Configurable themes** — colours, fonts, cover pages, logos, and organisation details bundled as self-contained theme directories
- **GitHub-style alerts** — `[!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`, and `[!CAUTION]` callout boxes with coloured borders and icons
- **Landscape sections** — mix portrait and landscape pages in a single document for wide tables and diagrams
- **Multi-chapter combines** — merge multiple Markdown files into one document with chapter dividers, driven by a YAML config
- **Cover pages** — SVG-based cover page templates with placeholder substitution for titles, version, author, and logo
- **Classification levels** — four built-in levels (`[RESTRICTED]`, `[INTERNAL]`, `[CONFIDENTIAL]`, `[PUBLIC]`) with automatic distribution notices
- **Footnote compaction** — duplicate footnotes with identical text are automatically merged into combined entries
- **SVG replacements** — swap ASCII art blocks for proper SVG diagrams during build

## Quick Example

```bash
pdg build report.md --pdf
```

This converts `report.md` (with YAML front-matter) into styled HTML and then renders a PDF. The output includes a branded cover page, table of contents, and document footer.

> **Note:** `pdg` is a short alias for `phoenix-docgen`. Both commands are interchangeable.

## Documentation

- [Getting Started](getting-started.md) — installation, first build, and project layout
- [Front-Matter Reference](frontmatter.md) — all YAML front-matter fields and defaults
- [Themes](themes.md) — creating, configuring, and selecting themes
- [Multi-Chapter Combines](combine.md) — YAML config format for combined documents
- [Markdown Features](markdown-features.md) — alerts, landscape sections, page breaks, footnotes
- [Cover Pages and Classification](cover-and-classification.md) — SVG cover templates and classification levels
- [Footer Customisation](footer.md) — page footers, document footers, and distribution notices
- [CLI Reference](cli-reference.md) — full command-line option reference for `init`, `build`, and `combine`
