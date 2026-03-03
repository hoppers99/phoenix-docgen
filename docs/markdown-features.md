# Markdown Features

phoenix-docgen processes standard pandoc markdown with several additional
features for professional document authoring.  This page covers alerts,
landscape sections, page breaks, footnotes, tables, headings, blockquotes,
raw HTML, and SVG replacements.

---

## Alerts

GitHub-style callout boxes that draw attention to important information.
phoenix-docgen supports five alert types, each with a distinct colour and
icon.

### Block-Level Alerts

Write alerts as pandoc blockquotes with a type marker on the first line:

```markdown
> [!NOTE]
> Informational content the reader should be aware of.
```

```markdown
> [!TIP]
> A helpful suggestion or best practice.
```

```markdown
> [!IMPORTANT]
> Critical information the reader must not miss.
```

```markdown
> [!WARNING]
> A potential issue that could cause problems.
```

```markdown
> [!CAUTION]
> A dangerous action that could cause harm or data loss.
```

Each alert renders as a styled box with:

- A **coloured left border** (4pt).
- A **light grey background** (`#f8fafc`).
- A **bold title** with an SVG icon matching the alert type.
- Contained paragraph(s) at 10pt.

### Multi-Paragraph Alerts

Continue the blockquote with `>` on subsequent lines.  Blank `>` lines
separate paragraphs within the alert:

```markdown
> [!WARNING]
> First paragraph of the warning.
>
> Second paragraph with more detail.
```

### Alert Type Reference

| Type | Colour | Icon | Hex |
|------|--------|------|-----|
| `[!NOTE]` | Blue | Circle with "i" (info) | Theme primary (default `#2c3e50`) |
| `[!TIP]` | Green | Lightbulb | `#1a7f37` |
| `[!IMPORTANT]` | Purple | Circle with "!" (exclamation) | `#7d3c98` |
| `[!WARNING]` | Orange | Triangle with "!" | `#bf8700` |
| `[!CAUTION]` | Red | Octagon with "!" | `#cf222e` |

The `[!NOTE]` type uses the theme's primary colour so it blends with the
document's heading colours.  All other types use fixed semantic colours
that remain consistent across themes.

### Inline Glyphs

Place a bare type marker in running text to insert a small coloured icon
without a surrounding box:

```markdown
This action [!WARNING] may cause data loss.
Check the configuration [!IMPORTANT] before proceeding.
```

Inline glyphs render as 11pt icons matching the type's colour.  They are
useful for drawing the eye to a specific word or phrase without breaking
the text flow.

---

## Landscape Sections

Wrap content in a `landscape-section` div to rotate pages to A4 landscape.
This is ideal for wide tables, Gantt charts, or any content that benefits
from the extra horizontal space.

### Syntax

```markdown
<div class="landscape-section">

## Wide Tables

| Column 1 | Column 2 | Column 3 | Column 4 | Column 5 |
|----------|----------|----------|----------|----------|
| data     | data     | data     | data     | data     |

</div>
```

### What Happens

- A **page break** is inserted before the landscape section
  (`page-break-before: always`).
- Pages switch to **A4 landscape** orientation.
- Margins tighten to **15mm** on all sides (compared to 20mm left/right and
  20mm top / 25mm bottom in portrait) to maximise content width.
- Page footers (page number, document title, classification marker) continue
  on landscape pages.
- After the closing `</div>`, the document **returns to portrait
  automatically**.

### Tables in Landscape Sections

Tables inside `.landscape-section` use `table-layout: fixed` with
`width: 100%`, which means columns fill the available width and their widths
are controlled by CSS rather than cell content.  Long text wraps
(`word-wrap: break-word`) instead of expanding the column.

By default, pandoc generates equal-width columns.  phoenix-docgen overrides
these with `width: auto !important` on all `col` elements so the browser can
distribute space naturally.

#### Custom Column Widths

For fine control, specific column widths are set in `shared_styles.py` using
`col:nth-child()` selectors scoped to table position within the landscape
section:

```css
/* First table in the landscape section */
.landscape-section table:first-of-type col:nth-child(1) { width: 7% !important; }
.landscape-section table:first-of-type col:nth-child(3) { width: 3% !important; }

/* Second table in the landscape section */
.landscape-section table:nth-of-type(2) col:nth-child(1) { width: 4% !important; }
```

Columns without explicit width rules split the remaining space equally.
To customise these widths for your documents, edit the `get_content_css()`
function in `shared_styles.py`.

### Multiple Landscape Sections

You can have multiple landscape sections in one document.  Each triggers its
own page break and landscape rotation.  Portrait content between them renders
normally.

---

## Page Breaks

Force a page break between any two blocks of content:

```html
<div style="page-break-after: always; break-after: page;"></div>
```

The dual property (`page-break-after` + `break-after`) ensures compatibility
across rendering engines.

### When to Use

- Between major sections that should start on a new page.
- Before appendices.
- Between landscape tables within a single landscape section.
- Before the Document Control table at the end of a document.

---

## Footnotes

### Syntax

Use standard pandoc footnote syntax.  Place `[^N]` markers in the text and
define them at the bottom of the file:

```markdown
This claim needs a source[^1].  Another assertion from the
same source[^2] and a different one[^3].

[^1]: Smith, J. (2025). *Example Reference*. Publisher.
[^2]: Smith, J. (2025). *Example Reference*. Publisher.
[^3]: Jones, A. (2024). *Another Reference*. Publisher.
```

In-text references render as superscript links.  The footnote section appears
at the end of the document (or chapter in combined mode) with a thin top
border.

### Automatic Duplicate Compaction

When multiple footnotes have identical text (e.g. the same source cited
several times), phoenix-docgen automatically merges them into a single entry
showing all reference numbers:

```
[1][2] Smith, J. (2025). Example Reference. Publisher.  ↩ ↩
[3]    Jones, A. (2024). Another Reference. Publisher.   ↩
```

- All in-text superscript markers remain in place (readers still see
  `[1]` and `[2]` in the body text).
- In-text links for merged footnotes are redirected to the primary entry.
- Backlinks (`↩`) from the merged entry point back to **every** original
  reference location.

### Styling

- In-text reference links use the theme's primary colour with 500 weight.
- The footnote section uses 9pt text with `#555555` colour and 1.4 line
  height.
- Compacted footnote number labels (e.g. `[1][2]`) are rendered in the
  primary colour with 600 weight.

---

## Tables

### Syntax

Standard markdown pipe tables:

```markdown
| Header 1 | Header 2 | Header 3 |
|----------|----------|----------|
| Cell     | Cell     | Cell     |
| Cell     | Cell     | Cell     |
```

### Styling

Tables are styled automatically with:

- **Dark header row:** theme secondary colour background with white text
  (600 weight).
- **Alternating row striping:** even rows get a light grey background
  (`#f5f5f5`).
- **Light borders:** `0.5pt solid #cccccc` between cells.
- **Full width:** tables span 100% of the content area.
- **10pt font size** for compact data presentation.

### Tables in Landscape Sections

In landscape sections, tables additionally receive:

- `table-layout: fixed` -- column widths are enforced by CSS.
- `width: 100%` -- fills the full landscape page width.
- `word-wrap: break-word` -- long content wraps rather than overflowing.

See [Landscape Sections](#landscape-sections) for details on customising
column widths.

---

## Headings

Use standard markdown headings.  They are styled by level:

| Level | Size | Colour | Style | Usage |
|-------|------|--------|-------|-------|
| `# H1` | 20pt | Primary | 500 weight | Document title |
| `## H2` | 16pt | Primary | 500 weight, bottom border | Main sections (included in TOC) |
| `### H3` | 14pt | Secondary | 500 weight | Subsections (included in TOC at default depth) |
| `#### H4` | 12pt | Secondary | 500 weight | Sub-subsections |

- **H1** uses the theme's primary colour with an 18pt top margin.
- **H2** uses the theme's primary colour with a 1px `#E2E8F0` bottom border.
  These are the main structural sections and always appear in the table of
  contents.
- **H3** uses the theme's secondary colour.  Included in the TOC when
  `toc_depth` is 3 or higher (the default).
- **H4** uses the theme's secondary colour at a smaller size.

All heading levels have `page-break-after: avoid` to prevent a heading from
appearing as the last line on a page.

---

## Blockquotes

Standard blockquotes (those not recognised as alerts) are styled with:

- A **4pt left border** in the theme's accent colour.
- A **light grey background** (`#f8fafc`).
- **10pt** font size in `#666666`.
- 8pt vertical margin and 12pt horizontal padding.

```markdown
> This is a standard blockquote.  It will receive the accent-coloured
> left border and grey background.
```

If the first line of the blockquote is a recognised alert marker
(e.g. `[!NOTE]`), it is converted to an alert box instead.

---

## Raw HTML

Any HTML in the markdown source passes through pandoc into the final output.
This is useful for:

- **Landscape section divs** -- `<div class="landscape-section">...</div>`
- **Page breaks** -- `<div style="page-break-after: always; break-after: page;"></div>`
- **SVG diagrams** -- embedded directly or via SVG replacement rules
- **Custom styling** -- inline `style` attributes for one-off formatting
- **Line breaks** -- `<br>` tags for manual line control within a paragraph

---

## SVG Replacements

SVG replacements let you author diagrams as ASCII art in your markdown
(which renders readably in plain text and version control diffs) and have
phoenix-docgen swap them for polished SVG graphics at build time.

### Configuration

Add an `svg_replacements` list to your YAML front-matter (single document)
or to a chapter entry (combined document):

```yaml
svg_replacements:
  - ascii_pattern: '<pre><code>.*?architecture.*?</code></pre>'
    svg_file: "diagrams/architecture.svg"
    notes_pattern: '<p><em>Diagram notes:\s*(.*?)</em></p>'
```

### Fields

| Field | Required | Description |
|-------|----------|-------------|
| `ascii_pattern` | Yes | Regex matched against the HTML output.  Typically targets a `<pre><code>` block containing your ASCII art. |
| `svg_file` | Yes | Path to the replacement SVG file (relative to the markdown file for single docs, or relative to the config file for combined docs). |
| `notes_pattern` | No | Regex to extract diagram notes text.  The first capture group is parsed into a bulleted list. |

### How It Works

1. pandoc converts your markdown to HTML, turning ASCII art fenced code
   blocks into `<pre><code>...</code></pre>` elements.
2. phoenix-docgen applies each `ascii_pattern` regex against the HTML output.
3. Matches are replaced with the SVG file content wrapped in a
   `<div class="diagram-container">` block.
4. If `notes_pattern` is provided and matches, the captured text is split on
   ` - ` boundaries (items starting with a capital letter) and rendered as a
   styled `<div class="diagram-notes">` block with a "Diagram Notes:" heading
   and bulleted list.

### Example

In your markdown:

````markdown
```
┌─────────────┐     ┌─────────────┐
│  Service A  │────▶│  Service B  │
└─────────────┘     └─────────────┘
```

*Diagram notes: Service A handles inbound requests - Service B processes background jobs - Communication is via message queue*
````

In your front-matter:

```yaml
svg_replacements:
  - ascii_pattern: '<pre><code>┌─.*?</code></pre>'
    svg_file: "diagrams/services.svg"
    notes_pattern: '<p><em>Diagram notes:\s*(.*?)</em></p>'
```

The ASCII block is replaced with the SVG graphic, and the italic notes
paragraph is converted into a styled notes panel:

> **Diagram Notes:**
> - Service A handles inbound requests
> - Service B processes background jobs
> - Communication is via message queue

### Styling

- `.diagram-container` -- 16pt vertical margin, `page-break-inside: avoid`.
- `.diagram-notes` -- light grey background (`#f8fafc`), 1px `#E2E8F0`
  border, 4pt border radius, 9.5pt font size.
- SVG elements receive 12pt vertical margin and `page-break-inside: avoid`.
