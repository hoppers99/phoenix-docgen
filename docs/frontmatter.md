# Front-Matter Reference

## What is front-matter?

Front-matter is a block of YAML metadata placed at the very top of a Markdown
file, enclosed between two `---` markers. phoenix-docgen reads this block before
processing the document body, using it to control the cover page, info block,
footer, table of contents, and other document-wide settings.

```yaml
---
title_line1: "INFRASTRUCTURE"
title_line2: "REVIEW"
version: "v1.0 FINAL"
---

# 1. Introduction

Your document body starts here ...
```

All fields are optional. Any field you omit falls back through the metadata
priority chain described below.


## Metadata priority order

When the same field is set in more than one place, the highest-priority source
wins:

| Priority | Source                 | Example                                  |
|----------|------------------------|------------------------------------------|
| 1 (highest) | CLI flags           | `--version "v2.0 FINAL"`                |
| 2        | YAML front-matter      | `version: "v2.0 FINAL"` between `---`   |
| 3        | Theme defaults         | `defaults.author` in `theme.yaml`        |
| 4 (lowest) | Built-in defaults   | Hard-coded fallbacks in phoenix-docgen   |

Theme defaults only override built-in defaults for three fields: `subtitle`,
`author`, and `classification`. All other fields fall straight through from
built-in defaults when not set elsewhere.


## Complete field reference

| Field                | Type           | Default               | Description |
|----------------------|----------------|-----------------------|-------------|
| `title_line1`        | string         | `"DOCUMENT"`          | First line of the cover page title. Uppercased on cover. Also used to derive `doc_title` if not set. |
| `title_line2`        | string         | `"TITLE"`             | Second line of the cover page title. Uppercased on cover. Also used to derive `doc_title` if not set. |
| `subtitle`           | string         | `""` (from theme)     | Subtitle below the title on the cover page. Uppercased on cover. Typically set to the organisation name in a theme. |
| `version`            | string         | `"v0.1 DRAFT"`        | Version string shown on the cover page and in the info block. Free-form — e.g. `"v2.0 FINAL"`, `"v1.1 DRAFT — 15/03/2026"`. |
| `doc_type`           | string         | `"Report"`            | Document type shown in the info block (e.g. `"Strategy Framework"`, `"Risk Assessment"`, `"Policy"`). Not displayed on the cover. |
| `classification`     | string         | `"[RESTRICTED]"`      | Security classification. Appears on the cover, info block, page margins, and footer. Accepts flexible input — see normalisation rules below. |
| `author`             | string         | `""` (from theme)     | Author line on the cover page. Uppercased on cover. Shown in the info block. |
| `year`               | string         | Current year          | Year badge on the cover page. Defaults to the year when the build runs. |
| `theme`              | string         | *(none)*              | Theme name to use for this document (e.g. `"acme"`). Overridden by the `--theme` CLI flag. See the [themes documentation](themes.md) for the full selection priority. |
| `toc`                | boolean        | `true`                | Whether to generate a table of contents. Disable with `toc: false` or `--no-toc`. |
| `toc_depth`          | integer        | `3`                   | Maximum heading level included in the table of contents (1--6). A value of `3` includes H1, H2, and H3. |
| `info_block`         | boolean        | `true`                | Whether to render the metadata info block after the cover page. The block shows document type, classification, version, date, and author. Disable with `info_block: false` or `--no-info-block`. |
| `cover`              | boolean        | `true`                | Whether to render the SVG cover page and blank verso. Disable with `cover: false` or `--no-cover`. |
| `doc_title`          | string         | *(derived)*           | Text displayed in the centre of every page footer. If not set, derived automatically from `title_line1` and `title_line2`. |
| `doc_id`             | string         | *(none)*              | Short document identifier prefix (e.g. `"A1"`, `"Ch3"`). Used in multi-chapter mode for chapter divider labels. |
| `distribution_notice`| string         | *(auto)*              | Overrides the auto-generated distribution notice in the document footer. Set to an empty string (`""`) to suppress the notice entirely. See `phoenix-docgen help classification` for auto-generated notices per level. |
| `footer_extra_lines` | list of strings| `[]`                  | Additional lines appended (in italics) to the document footer. See format details below. |
| `header_pattern`     | string (regex) | *(none)*              | Regular expression used to strip an unwanted section from the pandoc HTML output. See details below. |
| `svg_replacements`   | list of objects| `[]`                  | Rules for replacing ASCII-art diagrams in the HTML with SVG files. See format details below. |


## Complete example

The following front-matter block demonstrates every available field:

```yaml
---
title_line1: "INFRASTRUCTURE"
title_line2: "REVIEW"
subtitle: "GREENFIELD CONSULTING LTD"
version: "v2.0 FINAL"
doc_type: "Strategy Framework"
classification: "[CONFIDENTIAL]"
author: "ALEX MORGAN — PRINCIPAL ENGINEER"
year: "2026"
theme: greenfield
toc: true
toc_depth: 3
info_block: true
cover: true
doc_title: "Infrastructure Review — Greenfield Consulting"
doc_id: "IR1"
distribution_notice: "For Board members only — do not copy"
footer_extra_lines:
  - "Distribution: Board of Directors"
  - "Printed copies are uncontrolled"
header_pattern: "^Scope.*"
svg_replacements:
  - ascii_pattern: '<pre><code>.*?network-diagram.*?</code></pre>'
    svg_file: "diagrams/network-overview.svg"
  - ascii_pattern: '<pre><code>.*?flow-diagram.*?</code></pre>'
    svg_file: "diagrams/data-flow.svg"
    notes_pattern: '<p>Diagram notes:\s*(.*?)</p>'
---
```


## Field details

### classification — normalisation rules

The `classification` field accepts several input formats, all of which are
normalised to a consistent bracketed, uppercase form:

| Input                    | Normalised output |
|--------------------------|-------------------|
| `RESTRICTED`             | `[RESTRICTED]`    |
| `[RESTRICTED]`           | `[RESTRICTED]`    |
| `"[RESTRICTED]"`         | `[RESTRICTED]`    |
| `restricted`             | `[RESTRICTED]`    |
| `Confidential`           | `[CONFIDENTIAL]`  |

The normalisation process:

1. Strip surrounding quotes (`"` or `'`).
2. Strip square brackets (`[` and `]`).
3. Convert to uppercase.
4. Re-wrap in square brackets.

Four classification levels have automatic distribution notices:

| Level            | Auto distribution notice                          |
|------------------|---------------------------------------------------|
| `[RESTRICTED]`   | Not for distribution outside review team           |
| `[INTERNAL]`     | For internal use only                              |
| `[CONFIDENTIAL]` | For designated recipients only                     |
| `[PUBLIC]`       | *(no notice)*                                      |

Use `distribution_notice` to override or suppress the automatic text.


### footer_extra_lines

A YAML list of strings. Each string is rendered as an italic paragraph below
the standard document footer content.

```yaml
footer_extra_lines:
  - "Distribution: Review team only"
  - "Printed copies are uncontrolled"
```

These lines appear in the order listed, after the classification and
distribution notice.


### header_pattern

A regular expression string. phoenix-docgen searches the pandoc HTML output for
an `<h2>` element whose text matches this pattern, then removes everything from
that `<h2>` through the next `<hr>` element (inclusive). This is useful for
stripping auto-generated header sections that should not appear in the final
output.

```yaml
header_pattern: "^Scope.*"
```

Only the first match is removed (`count=1`). The pattern is matched with
`re.DOTALL` so `.` also matches newlines.


### svg_replacements

A list of objects, each describing a substitution rule for replacing ASCII-art
code blocks in the rendered HTML with proper SVG diagrams.

Each object supports these keys:

| Key              | Required | Description |
|------------------|----------|-------------|
| `ascii_pattern`  | Yes      | Regex matching the HTML code block to replace (typically a `<pre><code>...</code></pre>` block). Matched with `re.DOTALL`. |
| `svg_file`       | Yes      | Path to the replacement SVG file, relative to the Markdown source file's directory. |
| `notes_pattern`  | No       | Regex with one capture group, used to find and reformat diagram notes near the replaced block. Notes are converted into a styled list. |

```yaml
svg_replacements:
  - ascii_pattern: '<pre><code>.*?architecture.*?</code></pre>'
    svg_file: "diagrams/architecture.svg"
    notes_pattern: '<p>Diagram notes:\s*(.*?)</p>'
```

The SVG content is read from the file and wrapped in a
`<div class="diagram-container">` element. If `notes_pattern` is provided and
matches, the captured text is split on ` - ` boundaries and rendered as a
bulleted list under a "Diagram Notes" heading.
