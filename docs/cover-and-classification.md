# Cover Pages and Classification

## Cover page overview

phoenix-docgen generates a full-page cover from an SVG template bundled with the
active theme. At build time the template's placeholder tokens are replaced with
metadata drawn from YAML front-matter (or CLI flags), then the result is embedded
inline in the HTML output. The cover includes the document title, subtitle,
author, version, year badge, classification marker, organisation footer, and a
base64-embedded logo.

The cover page is always the first page of the rendered document. It is followed
by a [blank verso page](#blank-verso-page) so that the first content page falls
on a right-hand (recto) page when the document is printed double-sided.


## SVG template placeholders

The SVG template is an Inkscape-format A4 file (210 mm x 297 mm) stored in
the theme directory as `cover-page-template-a4.svg`. It contains the following
placeholder tokens, each replaced at build time by `cover_utils.fill_cover_svg`:

| Placeholder          | Filled from front-matter field | Notes |
|----------------------|-------------------------------|-------|
| `{{TITLE_LINE1}}`    | `title_line1`                 | Uppercased before substitution. |
| `{{TITLE_LINE2}}`    | `title_line2`                 | Uppercased before substitution. |
| `{{SUBTITLE}}`       | `subtitle`                    | Uppercased before substitution. |
| `{{AUTHOR}}`         | `author`                      | Uppercased before substitution. |
| `{{VERSION}}`        | `version`                     | Inserted verbatim (e.g. `"v1.0 DRAFT"`). |
| `{{CLASSIFICATION}}` | `classification`              | [Normalised](#classification-normalisation) before substitution. |
| `{{YEAR}}`           | `year`                        | Defaults to the current year at build time. |
| `{{ORG_FOOTER}}`     | Theme `organisation.name` + `organisation.address` | Rendered as `"Name \| Address"`. Empty when no theme is active. |

**Minimal front-matter example:**

```yaml
---
title_line1: "SECURITY"
title_line2: "AUDIT"
subtitle: "ACME CORP"
author: "ALEX MORGAN — PRINCIPAL ENGINEER"
version: "v1.0 DRAFT"
classification: "[OFFICIAL]"
year: "2026"
---
```

All fields are optional. Unset fields fall through the
[metadata priority chain](frontmatter.md#metadata-priority-order) (CLI flags
> front-matter > theme defaults > built-in defaults).


## Logo embedding

The organisation logo is embedded into the SVG cover as a base64-encoded
`<image>` element. At build time `cover_utils` performs the following steps:

1. Resolve the logo file path from `cover.logo` in `theme.yaml` (relative to
   the theme directory).
2. Read the file and encode it as a base64 data URI (`data:image/png;base64,...`).
3. Create an SVG `<image>` element positioned according to the theme's
   `cover.logo_position` values.
4. Insert the element immediately before the closing `</svg>` tag.

### Logo position

Logo placement is configured in `theme.yaml` under the `cover` section:

```yaml
cover:
  template: "cover-page-template-a4.svg"
  logo: "logo.png"
  logo_position: { x: 85, y: 75, width: 108, height: 108 }
```

| Key      | Type    | Description |
|----------|---------|-------------|
| `x`      | number  | Horizontal offset in SVG user units (pixels at 96 dpi). |
| `y`      | number  | Vertical offset in SVG user units. |
| `width`  | number  | Rendered width of the logo. |
| `height` | number  | Rendered height of the logo. |

The image element uses `preserveAspectRatio="xMidYMid meet"`, so the logo
scales proportionally within the specified bounding box.

### Fallback behaviour

When no theme is active, phoenix-docgen falls back to a built-in logo at
`src/templates/logo.png` with a default position of
`{ x: 85, y: 75, width: 108, height: 108 }`. If the logo file does not exist
at the resolved path, the logo is silently omitted and the cover renders
without it.


## Disabling the cover page

The cover page (and its accompanying blank verso) can be omitted entirely.

**CLI flag:**

```bash
phoenix-docgen build report.md --no-cover --pdf
```

**Front-matter:**

```yaml
---
cover: false
---
```

When the cover is disabled, the document begins directly with the info block
(if enabled) or the document body. The blank verso page is also suppressed.


## Blank verso page

Immediately after the cover, phoenix-docgen inserts a blank page containing
the centred text:

> This page is intentionally blank.

This ensures that the first content page starts on a recto (right-hand) page
when the document is printed double-sided. The verso page carries the same
page footer as every other page — document title in the centre, page number,
and classification marker.

The blank verso is generated automatically whenever the cover is enabled and is
suppressed when the cover is disabled (`cover: false` or `--no-cover`).


## Classification levels

phoenix-docgen recognises four classification levels. Each level carries a
default distribution notice that appears in the document footer.

| Level              | Default distribution notice                                |
|--------------------|------------------------------------------------------------|
| `[OFFICIAL]`       | Approved for general distribution                          |
| `[SENSITIVE]`      | Internal use only — not for external distribution          |
| `[RESTRICTED]`     | Restricted distribution — authorised recipients only       |
| `[CONFIDENTIAL]`   | Strictly confidential — named recipients only              |

### Where classification appears

Classification is displayed in four locations throughout the document:

1. **Cover page** — classification badge on the cover SVG.
2. **Page margins** — alternating left/right marker on every page.
3. **Info block** — classification field in the metadata block after the cover.
4. **Document footer** — classification level followed by the distribution
   notice.


## Classification normalisation

The `classification` field accepts flexible input. All of the following are
normalised to the same canonical form:

| Input                | Normalised output |
|----------------------|-------------------|
| `OFFICIAL`           | `[OFFICIAL]`      |
| `[OFFICIAL]`         | `[OFFICIAL]`      |
| `"[OFFICIAL]"`       | `[OFFICIAL]`      |
| `official`           | `[OFFICIAL]`      |
| `Sensitive`          | `[SENSITIVE]`     |
| `restricted`         | `[RESTRICTED]`    |
| `CONFIDENTIAL`       | `[CONFIDENTIAL]`  |

The normalisation algorithm (in `normalise_classification`):

1. Strip surrounding whitespace.
2. Strip surrounding quotes (`"` or `'`).
3. Strip square brackets (`[` and `]`).
4. Convert to uppercase.
5. Re-wrap in square brackets.

This means authors do not need to remember the exact casing or bracket syntax
when setting the classification in front-matter.

**Example:**

```yaml
---
classification: sensitive
---
```

This is normalised to `[SENSITIVE]` everywhere it appears in the output.


## Distribution notice

Each classification level has a default distribution notice (see the
[classification levels table](#classification-levels) above). The notice is
appended to the classification marker in the document footer — for example:

```
Classification: SENSITIVE — Internal use only — not for external distribution
```

### Overriding the distribution notice

Set the `distribution_notice` front-matter field to replace the automatic text
with a custom message:

```yaml
---
classification: "[RESTRICTED]"
distribution_notice: "For Board members only — do not copy"
---
```

This produces:

```
Classification: RESTRICTED — For Board members only — do not copy
```

The same field is available as a top-level key in multi-chapter combine
configs.

### Suppressing the distribution notice

Set `distribution_notice` to an empty string to remove the notice entirely,
leaving only the classification level in the footer:

```yaml
---
classification: "[RESTRICTED]"
distribution_notice: ""
---
```

This produces:

```
Classification: RESTRICTED
```

An explicit empty string is required. Omitting the field entirely will cause
the automatic notice for the current classification level to be used.
