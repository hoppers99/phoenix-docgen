# Theme System

## What are themes?

A theme is a self-contained directory that bundles an organisation's visual
identity for phoenix-docgen: colours, fonts, a cover page SVG template, a logo,
and default metadata values. Themes allow the same phoenix-docgen installation
to produce documents branded for different organisations simply by switching the
active theme.

When no theme is loaded, phoenix-docgen falls back to sensible built-in
defaults (neutral colours, system sans-serif fonts, no logo or cover template).


## Theme directory structure

Each theme lives in its own directory inside a themes root folder. The minimum
contents are a `theme.yaml` configuration file and, for full branding, an SVG
cover template, a logo image, and font files.

```
themes/
  acme/
    theme.yaml                    # Theme configuration (required)
    cover-page-template-a4.svg    # SVG cover with {{PLACEHOLDER}} tokens
    logo.png                      # Organisation logo (PNG recommended)
    fonts/
      LICENCE.txt                 # Font licence file
      Calibri-Regular.ttf
      Calibri-Bold.ttf
```

The `theme.yaml` file is the only strictly required file. Cover template, logo,
and fonts are optional but needed for full branded output.


## theme.yaml schema

Below is a complete `theme.yaml` with every section and field explained.

```yaml
name: "acme"
display_name: "Acme Corporation"

organisation:
  name: "ACME CORPORATION LTD"
  short_name: "Acme Corp"
  address: "42 Commerce Street, Wellington 6011"

defaults:
  subtitle: "ACME CORPORATION LTD"
  author: "ALEX MORGAN — PRINCIPAL ENGINEER"
  classification: "[RESTRICTED]"

colours:
  primary: "#1a5276"
  secondary: "#2c3e50"
  accent: "#27ae60"

fonts:
  family: "Calibri"
  fallback: "'Segoe UI', Arial, sans-serif"
  weights:
    400: "Calibri-Regular.ttf"
    700: "Calibri-Bold.ttf"

cover:
  template: "cover-page-template-a4.svg"
  logo: "logo.png"
  logo_position: { x: 85, y: 75, width: 108, height: 108 }
```

### name / display_name

| Field          | Type   | Description |
|----------------|--------|-------------|
| `name`         | string | Internal theme identifier, typically matching the directory name (e.g. `"acme"`). If omitted, defaults to the directory name. |
| `display_name` | string | Human-readable name shown in build output (e.g. `"Acme Corporation"`). If omitted, defaults to `name`. |


### organisation

Organisation details used in the info block, document footer, and cover page
`ORG_FOOTER` placeholder.

| Field        | Type   | Description |
|--------------|--------|-------------|
| `name`       | string | Full legal name, typically uppercase (e.g. `"ACME CORPORATION LTD"`). Shown in the info block and document footer. |
| `short_name` | string | Abbreviated name (e.g. `"Acme Corp"`). Used when deriving the default `doc_title` for page footers. |
| `address`    | string | Street address or location line. Available for cover page templates. |

Built-in fallback: all three default to empty strings when no theme is loaded.


### defaults

Override the built-in default values for document metadata. These sit below
front-matter and CLI flags in the [metadata priority chain](frontmatter.md#metadata-priority-order),
so a theme can set organisation-wide defaults while individual documents can
still override them.

| Field            | Type   | Built-in fallback | Description |
|------------------|--------|-------------------|-------------|
| `subtitle`       | string | `""`              | Default subtitle for the cover page when not set in front-matter. Typically the organisation name. |
| `author`         | string | `""`              | Default author line for the cover page and info block. |
| `classification` | string | `"[RESTRICTED]"`  | Default classification level. Subject to normalisation rules (see [front-matter docs](frontmatter.md#classification--normalisation-rules)). |


### colours

Three colour values (CSS hex format) that control the document's visual palette.

| Colour      | Built-in fallback | Used for |
|-------------|-------------------|----------|
| `primary`   | `#2c3e50`         | Headings (H1, H2), hyperlinks, table of contents entries, footnote reference numbers. |
| `secondary` | `#34495e`         | Table header row backgrounds, chapter divider backgrounds, footer border, organisation name in the document footer. |
| `accent`    | `#2980b9`         | Blockquote left border, cover page swish gradient. |


### fonts

Font configuration for the document body and headings.

| Field      | Type   | Built-in fallback                  | Description |
|------------|--------|------------------------------------|-------------|
| `family`   | string | `"sans-serif"`                     | CSS font-family name for the primary font (e.g. `"Calibri"`, `"Inter"`). |
| `fallback` | string | `"Arial, Helvetica, sans-serif"`   | CSS fallback font stack, appended after the primary family. |
| `weights`  | object | *(none)*                           | Mapping of CSS font-weight numbers to TTF filenames relative to the `fonts/` subdirectory. |

The `weights` mapping tells phoenix-docgen which font files to embed. Each key
is a numeric weight (e.g. `400` for regular, `700` for bold) and each value is
the filename of the corresponding TTF file inside the theme's `fonts/`
directory:

```yaml
fonts:
  family: "Inter"
  fallback: "'Segoe UI', Arial, sans-serif"
  weights:
    400: "Inter-Regular.ttf"
    700: "Inter-Bold.ttf"
```

The full CSS `font-family` value is assembled as: `'Inter', 'Segoe UI', Arial, sans-serif`.

Only font files that actually exist on disc are loaded; missing files are
silently skipped.


### cover

Cover page asset references and logo positioning.

| Field           | Type   | Default                                | Description |
|-----------------|--------|----------------------------------------|-------------|
| `template`      | string | `"cover-page-template-a4.svg"`         | Filename of the SVG cover page template, relative to the theme directory. The template is an Inkscape-compatible A4 SVG (210 mm x 297 mm) containing `{{PLACEHOLDER}}` tokens that phoenix-docgen fills at build time. |
| `logo`          | string | `"logo.png"`                           | Filename of the organisation logo, relative to the theme directory. Embedded into the cover SVG as a base64-encoded image element. |
| `logo_position` | object | `{ x: 85, y: 75, width: 108, height: 108 }` | Position and dimensions (in SVG user units) for the logo on the cover page. Keys: `x`, `y`, `width`, `height`. |


## Theme selection priority

phoenix-docgen checks six sources when determining which theme to use, in
order from highest to lowest priority:

| Priority | Source                 | How to set                                        |
|----------|------------------------|---------------------------------------------------|
| 1        | CLI flag               | `--theme acme`                                    |
| 2        | Front-matter / config  | `theme: acme` in YAML front-matter or combine config |
| 3        | Environment variable   | `export PHOENIX_THEME=acme`                       |
| 4        | Global config          | `default_theme: acme` in config file              |
| 5        | Auto-detect            | If exactly one theme directory exists, it is used  |
| 6        | None                   | Built-in fallback (no theme loaded)               |

Auto-detection (level 5) scans the resolved themes directory for subdirectories
that contain a `theme.yaml` file. If there is exactly one such directory, that
theme is selected automatically. If there are zero or multiple theme
directories (and no higher-priority source is set), no theme is loaded and
built-in defaults apply.


## Themes directory discovery

phoenix-docgen checks four locations to find the themes root directory, in
order from highest to lowest priority:

| Priority | Source                 | How to set                                      |
|----------|------------------------|-------------------------------------------------|
| 1        | CLI flag               | `--themes-dir /path/to/themes`                  |
| 2        | Environment variable   | `export PHOENIX_THEMES_DIR=/path/to/themes`     |
| 3        | Global config          | `themes_dir: /path/to/themes` in config file    |
| 4        | Relative to scripts    | `themes/` directory beside (or one level above) the installed scripts |

At priority level 4, phoenix-docgen checks for a `themes/` directory adjacent
to its own `src/` directory, then one level up from `src/` (covering the common
repository layout where scripts are in `src/` and themes sit at the repository
root).


## Global configuration file

A global YAML configuration file lets you set a persistent themes directory
and default theme without passing CLI flags or environment variables on every
build.

### File location

| Platform       | Default path                                         | Override |
|----------------|------------------------------------------------------|----------|
| macOS / Linux  | `~/.config/phoenix-docgen/config.yaml`               | `PHOENIX_CONFIG` environment variable |
| Windows        | `%APPDATA%\phoenix-docgen\config.yaml`               | `PHOENIX_CONFIG` environment variable |

If `PHOENIX_CONFIG` is set, that path is used instead of the platform default.

### Schema

```yaml
# ~/.config/phoenix-docgen/config.yaml

themes_dir: ~/themes/phoenix-docgen
default_theme: acme
```

| Key             | Type   | Description |
|-----------------|--------|-------------|
| `themes_dir`    | string | Absolute or `~`-relative path to the directory containing theme subdirectories. |
| `default_theme` | string | Name of the theme to use when no `--theme` flag, front-matter `theme:` key, or `PHOENIX_THEME` environment variable is set. |

The file is entirely optional. If it does not exist, phoenix-docgen proceeds
without error — all values are treated as unset and lower-priority sources
take effect.


## Creating a new theme

1. **Copy an existing theme directory** (or create a new directory under your
   themes root):

   ```
   cp -r themes/existing themes/newbrand
   ```

2. **Edit `theme.yaml`** with the new organisation's details — name, colours,
   fonts, and defaults.

3. **Replace the SVG cover template.** The template must be an A4-sized SVG
   (210 mm x 297 mm) with `{{PLACEHOLDER}}` tokens that phoenix-docgen fills
   at build time:

   | Placeholder          | Filled from          |
   |----------------------|----------------------|
   | `{{TITLE_LINE1}}`    | `title_line1` (uppercased) |
   | `{{TITLE_LINE2}}`    | `title_line2` (uppercased) |
   | `{{SUBTITLE}}`       | `subtitle` (uppercased)    |
   | `{{AUTHOR}}`         | `author` (uppercased)      |
   | `{{VERSION}}`        | `version`                  |
   | `{{CLASSIFICATION}}` | `classification` (normalised) |
   | `{{YEAR}}`           | `year`                     |

4. **Replace the logo** with the organisation's logo image (PNG recommended).
   Update `cover.logo` and `cover.logo_position` in `theme.yaml` to match the
   new image's dimensions and desired placement.

5. **Add font files** to the `fonts/` subdirectory and update the `fonts.weights`
   mapping in `theme.yaml`. Include the font licence file.

6. **Test the theme** by building a document:

   ```
   phoenix-docgen build document.md --theme newbrand --pdf
   ```


## Using separate Git repositories for themes

The `themes/` directory is typically gitignored from the main phoenix-docgen
repository (it often contains organisation-specific assets that should not be
published alongside the tool). Each theme can be managed as its own Git
repository, cloned into the themes directory:

```
cd themes/
git clone git@github.com:example/phoenix-theme-acme.git acme
git clone git@github.com:example/phoenix-theme-greenfield.git greenfield
```

This keeps theme assets versioned independently of the tool itself and allows
different teams to maintain their own branding.


## Organisational deployment

For teams sharing the same themes across multiple machines, point `themes_dir`
in the global config to a shared location — a network drive, synced folder, or
a well-known local path that your provisioning tools populate:

```yaml
# ~/.config/phoenix-docgen/config.yaml
themes_dir: /opt/company/phoenix-themes
default_theme: corporate
```

Every user on the team then gets the same themes without needing to clone
repositories manually. Theme updates propagate through the shared directory.
