# phoenix-docgen

Branded document builder — converts Markdown to professionally styled HTML and PDF with configurable themes.

## Features

- **Markdown to PDF** via pandoc (Markdown → HTML) and WeasyPrint (HTML → PDF)
- **Configurable themes** — colours, fonts, cover page, logo, organisation details
- **SVG cover pages** — Inkscape-designed templates with placeholder substitution
- **GitHub-style alerts** — `[!NOTE]`, `[!WARNING]`, etc.
- **Mixed orientation** — portrait and landscape pages in a single document
- **Multi-chapter combines** — YAML config for combining multiple Markdown files
- **Built-in help** — `phoenix-docgen help [topic]` for comprehensive documentation

## Quick Start

### Prerequisites

- Python 3.9+
- [pandoc](https://pandoc.org/) (Markdown → HTML conversion)
- WeasyPrint and PyYAML (installed automatically in the venv)

### Install (macOS/Linux)

```bash
git clone <repo-url> ~/Development/phoenix-docgen
cd ~/Development/phoenix-docgen
./install.sh
```

This creates symlinks so changes in the repo are immediately available:
- `~/.local/bin/phoenix-docgen` → shell wrapper
- `~/.local/share/phoenix-docgen/*.py` → source files
- `~/.local/share/phoenix-docgen/themes/` → themes directory

### Install (Docker — Windows recommended, any platform)

Docker bundles Python, pandoc, WeasyPrint, and all native dependencies into a single image. This is the recommended path for Windows and available by choice on any platform.

```bash
docker pull ghcr.io/hoppers99/phoenix-docgen:latest
```

Copy the wrapper script to somewhere on your PATH:

- **macOS/Linux:** `cp docker/pdg-docker.sh ~/.local/bin/pdg-docker && chmod +x ~/.local/bin/pdg-docker`
- **Windows:** Copy `docker/pdg-docker.ps1` and `docker/pdg-docker.bat` to a directory on your PATH

Set your themes directory: `export PHOENIX_THEMES_DIR="$HOME/themes/phoenix-docgen"` (or the Windows equivalent — see [Docker documentation](docs/docker.md) for full setup).

### Install (Windows — Native)

If you prefer a native installation on Windows without Docker:

1. Clone the repo
2. Create a venv: `python -m venv %LOCALAPPDATA%\phoenix-docgen\venv`
3. Install dependencies: `pip install weasyprint pyyaml`
4. Copy or symlink source files to `%LOCALAPPDATA%\phoenix-docgen\`
5. Add `src\phoenix-docgen.bat` to your PATH

### Basic Usage

```bash
# Scaffold a new document
phoenix-docgen init report.md --title1 "AI" --title2 "STRATEGY"

# Build to HTML + PDF
phoenix-docgen build report.md --pdf

# Build with a specific theme
phoenix-docgen build report.md --theme mytheme --pdf

# Multi-chapter combine
phoenix-docgen combine --config project.yaml --pdf

# Help
phoenix-docgen help              # List all topics
phoenix-docgen help frontmatter  # Detailed frontmatter reference
```

## Themes

Themes are self-contained directories with a `theme.yaml` configuration file plus assets (SVG template, logo, fonts).

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

### Theme Selection

Themes are resolved in priority order (highest wins):

1. `--theme <name>` CLI flag
2. `theme: <name>` in YAML front-matter or combine config
3. `PHOENIX_THEME` environment variable
4. `default_theme` in `~/.config/phoenix-docgen/config.yaml`
5. Auto-detect (if exactly one theme exists)
6. Built-in defaults (backward compatible)

### Themes Directory

Where phoenix-docgen looks for themes (highest priority wins):

1. `--themes-dir <path>` CLI flag
2. `PHOENIX_THEMES_DIR` environment variable
3. `themes_dir` in `~/.config/phoenix-docgen/config.yaml`
4. `themes/` relative to the installed scripts

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

## Global Configuration

Location: `~/.config/phoenix-docgen/config.yaml`

```yaml
# Where to find theme directories
themes_dir: ~/themes/phoenix-docgen

# Default theme when none specified
default_theme: mytheme
```

Override with the `PHOENIX_CONFIG` environment variable to use a different config file path.

## Help Topics

Run `phoenix-docgen help` for a full list, or `phoenix-docgen help <topic>` for details:

- **frontmatter** — YAML front-matter field reference
- **alerts** — GitHub-style alert boxes
- **markdown** — Markdown authoring tips for phoenix-docgen
- **combine** — Multi-chapter document configuration
- **cover** — Cover page customisation
- **classification** — Document classification and distribution
- **landscape** — Landscape pages for wide tables
- **footer** — Footer customisation
- **branding** — Theme system and branding

## Licence

Source code: [MIT](LICENCE). Font licences are included with each theme (e.g., `fonts/LICENCE.txt`).

Themes are separate repositories with their own licensing.
