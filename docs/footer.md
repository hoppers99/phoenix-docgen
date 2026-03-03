# Footers

phoenix-docgen produces two distinct kinds of footer:

| Footer type      | Where it appears                  | Controlled by                          |
|------------------|-----------------------------------|----------------------------------------|
| **Page footer**  | Bottom margin of every page       | CSS `@page` rules; `doc_title`, `classification` |
| **Document footer** | End of the document body       | `build_footer()` function; `footer_extra_lines`, `distribution_notice` |

Both are generated automatically. The page footer requires no configuration
beyond the standard front-matter fields; the document footer can be customised
with a handful of optional fields.


## Page footer

The page footer is rendered by the browser's paged-media engine using CSS
`@page` margin boxes. It appears on every page except the cover page.

### Layout

| Position        | Content                                 |
|-----------------|-----------------------------------------|
| Bottom centre   | `doc_title` text                        |
| Bottom left (even pages) / bottom right (odd pages) | Page number |
| Bottom right (even pages) / bottom left (odd pages) | Classification marker (e.g. `[RESTRICTED]`) |

On left-hand (even) pages the page number sits at bottom-left and the
classification marker at bottom-right. On right-hand (odd) pages the positions
swap. The document title always remains centred.

### Styling

All three page-footer elements share the same base styling:

- **Font size:** 10 pt
- **Font family:** the active theme's font stack (falls back to
  `Arial, Helvetica, sans-serif`)
- **Document title colour:** `#999999`
- **Page number colour:** `#666666`
- **Classification marker colour:** `#999999`, weight 600, with 1 pt letter
  spacing

### Special pages

| Page type     | Behaviour |
|---------------|-----------|
| Cover page (`@page:first` / `@page cover`) | All three footer slots suppressed — no title, no page number, no classification. |
| Blank verso (`@page blank`) | Document title and classification marker are shown; page number is suppressed. |
| Landscape pages (`@page landscape`) | Full footer with the same alternating layout as portrait pages, using the landscape margin dimensions. |


## Document footer

The document footer is a block of HTML rendered at the very end of the document
body, inside the content wrapper. It is separated from the preceding content by
a 2 pt horizontal rule in the theme's secondary colour.

### Content

The footer contains, in order:

1. **Organisation name and document title** — the organisation name (from the
   theme) in bold secondary colour, followed by a dash and the document title
   derived from `title_line1` and `title_line2`.
2. **Classification and distribution notice** — the uppercase classification
   level, optionally followed by a dash and the distribution notice text.
3. **Extra lines** — any strings provided in `footer_extra_lines`, each
   rendered as an italic paragraph.

### Styling

The document footer block uses the CSS class `.doc-footer`:

- **Top margin:** 36 pt
- **Top border:** 2 pt solid, theme secondary colour (default `#34495e`)
- **Text alignment:** centred
- **Font size:** 8 pt
- **Text colour:** `#666666`
- **Paragraph spacing:** 3 pt between lines


## `doc_title`

The `doc_title` field controls the text shown in the centre of every page
footer.

### Derivation

If `doc_title` is **set explicitly** in front-matter or combine config, that
value is used as-is:

```yaml
doc_title: "Infrastructure Review — Greenfield Consulting"
```

If `doc_title` is **not set**, it is derived automatically. The exact formula
depends on the build mode:

| Mode     | Auto-derived value |
|----------|--------------------|
| Single document (`build`) | `"{org_short} — {title_line1} {title_line2}"` (stripped) |
| Combined document (`combine`) | `"{org_short} — Combined Document"` |

Where `org_short` is the theme's `organisation.short_name` value.

### Where it appears

- **Page footer** — centre of every page (passed to CSS `@page @bottom-center`)
- **HTML `<title>` element** — in single-document mode the browser tab title is
  derived from the title lines and organisation short name; in combine mode it
  defaults to `doc_title` unless overridden by `html_title`

### CLI override

```
pdg build report.md --doc-title "Custom Footer Title" --pdf
```


## `footer_extra_lines`

A front-matter field that adds additional italic lines to the document footer,
below the classification and distribution notice.

### Format

A YAML list of strings. Each string becomes one centred, italic paragraph:

```yaml
footer_extra_lines:
  - "Distribution: Review team only"
  - "Printed copies are uncontrolled"
```

### Rendered output

Each line is wrapped in a `<p>` with `font-style: italic` and `margin-top: 6pt`.
The lines appear in the order listed, after the classification line.

### Default

An empty list — no extra lines are rendered unless you explicitly provide them.


## `distribution_notice`

Overrides the auto-generated distribution notice that appears on the
classification line in the document footer.

### Auto-generated notices

When `distribution_notice` is not set, the notice is derived from the
`classification` level:

| Classification    | Auto notice                                    |
|-------------------|------------------------------------------------|
| `[RESTRICTED]`    | Not for distribution outside review team        |
| `[INTERNAL]`      | For internal use only                           |
| `[CONFIDENTIAL]`  | For designated recipients only                  |
| `[PUBLIC]`        | *(no notice)*                                   |

### Custom notice

Provide a string to replace the auto-generated text:

```yaml
distribution_notice: "For Board members only — do not copy"
```

### Suppressing the notice

Set `distribution_notice` to an empty string to suppress it entirely:

```yaml
distribution_notice: ""
```

This removes the dash and notice text from the classification line, leaving
only the classification level itself.


## Combine mode footers

In multi-chapter documents built with the `combine` command, the document
footer is constructed from the combine config file rather than from individual
chapter front-matter.

### How it works

1. The `cover` section of the combine config provides the base metadata
   (`title_line1`, `title_line2`, `classification`, etc.).
2. `footer_extra_lines` is read from the **top-level** combine config (not from
   the `cover` section).
3. `distribution_notice` is read from the `cover` section alongside the
   classification level.
4. `doc_title` is read from the top-level combine config; if not set it
   defaults to `"{org_short} — Combined Document"`.

### Example combine config

```yaml
cover:
  title_line1: "PROJECT"
  title_line2: "COMPENDIUM"
  subtitle: "GREENFIELD CONSULTING LTD"
  version: "v1.0 FINAL"
  classification: "[CONFIDENTIAL]"
  author: "ALEX MORGAN — PRINCIPAL ENGINEER"
  year: "2026"

doc_title: "Project Compendium — Greenfield Consulting"
output: "Project-Compendium-Combined.html"

footer_extra_lines:
  - "Distribution: Steering Committee"
  - "Printed copies are uncontrolled"

# distribution_notice: ""   # uncomment to suppress

chapters:
  - source: "chapters/01-overview.md"
    title: "Project Overview"
  - source: "chapters/02-design.md"
    title: "Design Specification"
```

In this example the page footer on every page reads
*Project Compendium — Greenfield Consulting*, with `[CONFIDENTIAL]` alternating
in the opposite corner from the page number. The document footer at the end
shows the organisation name, document title, classification with the
auto-generated notice for CONFIDENTIAL, and both extra lines in italics.


## Quick reference

| Field                | Type            | Default          | Scope |
|----------------------|-----------------|------------------|-------|
| `doc_title`          | string          | *(derived)*      | Page footer centre text |
| `footer_extra_lines` | list of strings | `[]`             | Extra italic lines in document footer |
| `distribution_notice`| string          | *(auto from classification)* | Override or suppress the distribution notice |
| `classification`     | string          | `[RESTRICTED]`   | Classification marker in page footer and document footer |
