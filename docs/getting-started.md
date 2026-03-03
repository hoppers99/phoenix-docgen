# Getting Started

This guide walks through installing phoenix-docgen, scaffolding your first document, and building it to PDF.

## Prerequisites

- **Python 3.9+** — required for WeasyPrint and the build pipeline
- **pandoc** — handles Markdown-to-HTML conversion

Install pandoc via Homebrew (macOS):

```bash
brew install pandoc
```

On other platforms, see the [pandoc installation page](https://pandoc.org/installing.html).

## Installation

Clone the repository and run the installer:

```bash
git clone <repo-url> ~/Development/phoenix-docgen
cd ~/Development/phoenix-docgen
./install.sh
```

The install script performs the following steps:

1. **Symlinks source files** from `src/` into `~/.local/share/phoenix-docgen/` — this means changes in the repo are immediately available without re-installing
2. **Symlinks the themes directory** into the same location
3. **Creates the shell wrapper** at `~/.local/bin/phoenix-docgen` and a short alias `~/.local/bin/pdg`
4. **Creates a Python virtual environment** at `~/.local/share/phoenix-docgen/venv/` with WeasyPrint and PyYAML installed
5. **Creates a default config file** at `~/.config/phoenix-docgen/config.yaml` (if one does not already exist)

The wrapper script activates the virtual environment automatically, so you never need to manage it manually.

> **Note:** Ensure `~/.local/bin` is on your `PATH`. Most shells include it by default. If `pdg` is not recognised after installation, add `export PATH="$HOME/.local/bin:$PATH"` to your shell profile.

## Alternative: Docker Installation

If you prefer not to install Python, pandoc, and WeasyPrint natively — or you are on Windows where these dependencies can be difficult to manage — phoenix-docgen is available as a Docker image that bundles everything.

```bash
docker pull ghcr.io/hoppers99/phoenix-docgen:latest
```

See [Docker](docker.md) for full setup instructions, wrapper script installation, and usage.

## Verify the Installation

```bash
pdg --help
```

You should see the usage summary listing the `init`, `build`, `combine`, and `help` subcommands.

## Set Up a Theme

Themes provide branding: colours, fonts, cover page template, logo, and organisation details. Each theme is a self-contained directory. Clone or copy a theme into the themes directory:

```bash
cd ~/Development/phoenix-docgen/themes
git clone <theme-repo-url> mytheme
```

The theme directory should contain at minimum a `theme.yaml` file. A typical structure looks like:

```
themes/mytheme/
  theme.yaml                    # Theme configuration
  cover-page-template-a4.svg    # SVG cover with {{PLACEHOLDER}} tokens
  logo.png                      # Organisation logo
  fonts/
    LICENCE.txt                 # Font licence
    MyFont-Regular.ttf
    MyFont-Bold.ttf
```

You can set a default theme in `~/.config/phoenix-docgen/config.yaml`:

```yaml
default_theme: mytheme
```

See [Themes](themes.md) for the full `theme.yaml` schema and theme resolution order.

## Scaffold Your First Document

Use `pdg init` to create a Markdown file pre-filled with YAML front-matter and helpful inline comments:

```bash
pdg init report.md --title1 "MY" --title2 "REPORT"
```

This creates `report.md` with front-matter fields for title, subtitle, version, author, classification, and more. Open it in your editor and replace the placeholder body content with your own.

## Build to PDF

Once you have content in your Markdown file, build it:

```bash
pdg build report.md --pdf
```

This produces two output files alongside `report.md`:

- `report.html` — the styled HTML document
- `report.pdf` — the final PDF rendered by WeasyPrint

### Output Structure

A built document follows this structure from first page to last:

```
Cover Page  -->  Blank Verso  -->  Info Block  -->  Table of Contents  -->  Document Body  -->  Document Footer
```

| Section           | Description                                                        |
|-------------------|--------------------------------------------------------------------|
| Cover Page        | SVG-based page with title, subtitle, version, author, and logo     |
| Blank Verso       | Reverse of the cover — "This page is intentionally blank"          |
| Info Block        | Document type, classification, version, and date metadata          |
| Table of Contents | Auto-generated from headings (configurable depth)                  |
| Document Body     | Your Markdown content, converted and styled                        |
| Document Footer   | Organisation name, classification, and any extra footer lines      |

You can disable individual sections with `--no-cover`, `--no-info-block`, or `--no-toc`.

## Built-in Help

phoenix-docgen includes a topic-based help system covering all features in detail:

```bash
pdg help                  # List all available topics
pdg help frontmatter      # YAML front-matter field reference
pdg help alerts           # Alert boxes and inline glyphs
pdg help landscape        # Landscape sections for wide tables
pdg help combine          # Multi-chapter document configuration
```

## Next Steps

- [Front-Matter Reference](frontmatter.md) — understand every YAML field and its default
- [Themes](themes.md) — create your own theme or customise an existing one
- [Markdown Features](markdown-features.md) — alerts, landscape sections, page breaks, and footnotes
- [Multi-Chapter Combines](combine.md) — build large documents from multiple Markdown files
- [CLI Reference](cli-reference.md) — full command-line option reference
- [Docker](docker.md) — run phoenix-docgen via Docker (recommended for Windows)
