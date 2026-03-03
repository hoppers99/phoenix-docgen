# CLI Reference

Complete command-line reference for phoenix-docgen.

## Overview

`phoenix-docgen` is the main CLI entry point for building branded documents from Markdown. The short alias `pdg` is installed alongside it and is fully interchangeable — every example in this guide works with either name.

```bash
pdg <command> [options]
```

There are four subcommands:

| Command   | Purpose                                           |
|-----------|---------------------------------------------------|
| `init`    | Scaffold a new document or combine config file    |
| `build`   | Build a single Markdown file to HTML and/or PDF   |
| `combine` | Build a multi-chapter document from a YAML config |
| `help`    | Show detailed help on a specific topic            |

Running `pdg` with no subcommand prints the usage summary.

---

## `pdg init`

Scaffold a new Markdown document pre-filled with YAML front-matter, or create a YAML config file for multi-chapter builds.

```
pdg init [FILENAME] [--config FILE] [--chapters FILE ...] [options]
```

### Arguments

| Argument   | Required | Description                                           |
|------------|----------|-------------------------------------------------------|
| `FILENAME` | No       | Output Markdown file path (e.g. `report.md`)          |
| `--config` | No       | Create a YAML config file instead of a Markdown file  |
| `--chapters` | No     | Markdown files to include as chapters (config mode only). Accepts multiple files. |

Provide either a positional `FILENAME` (to scaffold a single document) or `--config` (to scaffold a combine config). When using `--config`, you may also pass `--chapters` to pre-populate the chapter list.

All [metadata override flags](#metadata-override-flags) and [theme flags](#theme-flags) are accepted.

### Examples

Scaffold a single document:

```bash
pdg init report.md
```

Scaffold with metadata pre-filled:

```bash
pdg init report.md --title1 "PROJECT" --title2 "PROPOSAL" --author "Jane Smith"
```

Scaffold a combine config with chapters:

```bash
pdg init --config project.yaml --chapters intro.md analysis.md conclusion.md
```

Scaffold a combine config using a specific theme:

```bash
pdg init --config project.yaml --theme mytheme --chapters ch1.md ch2.md
```

---

## `pdg build`

Build a single Markdown file into styled HTML and optionally PDF.

```
pdg build SOURCE [-o OUTPUT] [--pdf] [--no-cover] [--no-toc] [--no-info-block] [options]
```

### Arguments

| Argument              | Required | Description                                                                 |
|-----------------------|----------|-----------------------------------------------------------------------------|
| `SOURCE`              | Yes      | Source Markdown file                                                        |
| `-o`, `--output`      | No       | Override the output file path (default: input stem + `.html`)               |
| `--pdf`               | No       | Generate a PDF via WeasyPrint in addition to HTML                           |
| `--html`              | No       | Keep HTML output (this is the default when `--pdf` is not given)            |
| `--no-cover`          | No       | Skip cover page and blank verso generation                                  |
| `--no-toc`            | No       | Disable table of contents generation                                        |
| `--no-info-block`     | No       | Disable the metadata info block after the cover                             |
| `--header-pattern`    | No       | Regex pattern to strip from pandoc output (matches an H2 through the next HR) |

All [metadata override flags](#metadata-override-flags) and [theme flags](#theme-flags) are accepted.

### Examples

Build to HTML only (default):

```bash
pdg build report.md
```

Build to both HTML and PDF:

```bash
pdg build report.md --pdf
```

Build with a custom output filename:

```bash
pdg build report.md -o output/final-report.html --pdf
```

Override the version at build time:

```bash
pdg build report.md --version "v2.0 FINAL" --pdf
```

Build without the cover page:

```bash
pdg build report.md --no-cover --pdf
```

Build with a specific theme and classification:

```bash
pdg build report.md --theme mytheme --classification "[CONFIDENTIAL]" --pdf
```

---

## `pdg combine`

Build a multi-chapter document from multiple Markdown files, driven by a YAML configuration file.

```
pdg combine --config FILE [-o OUTPUT] [--pdf] [options]
```

### Arguments

| Argument         | Required | Description                                              |
|------------------|----------|----------------------------------------------------------|
| `--config`       | Yes      | Path to the YAML configuration file                      |
| `-o`, `--output` | No       | Override the output file path                             |
| `--pdf`          | No       | Generate a PDF via WeasyPrint in addition to HTML         |
| `--html`         | No       | Keep HTML output (this is the default when `--pdf` is not given) |

> **Note:** The `combine` subcommand does not accept metadata override flags on the command line. All metadata (title, author, classification, etc.) is set within the YAML config file's `cover:` section. See [Multi-Chapter Combines](combine.md) for the full config format.

### Examples

Build a combined document to PDF:

```bash
pdg combine --config project.yaml --pdf
```

Build with a custom output path:

```bash
pdg combine --config project.yaml -o output/combined.html --pdf
```

---

## `pdg help`

Display the built-in topic-based help system.

```
pdg help [TOPIC]
```

Running `pdg help` with no topic prints the full topic listing and quick-start examples. Running `pdg help <topic>` shows detailed reference for that topic.

### Available Topics

| Topic            | Description                                      |
|------------------|--------------------------------------------------|
| `frontmatter`    | YAML front-matter fields and defaults             |
| `alerts`         | GitHub-style alert boxes and inline glyphs        |
| `markdown`       | Markdown authoring features (landscape, page breaks, footnotes, tables, raw HTML) |
| `combine`        | Multi-chapter document configuration (YAML config)|
| `cover`          | Cover page, SVG template, and logo                |
| `classification` | Classification levels and distribution notices     |
| `landscape`      | Landscape sections and table column widths         |
| `footer`         | Document footer customisation                      |
| `branding`       | Theme system, multi-branding, and extensibility    |

### Examples

List all available topics:

```bash
pdg help
```

Show the front-matter field reference:

```bash
pdg help frontmatter
```

Show how to configure multi-chapter builds:

```bash
pdg help combine
```

---

## Common Flags

### Metadata Override Flags

The following flags are shared across the `init` and `build` subcommands. They override values set in YAML front-matter or theme defaults.

| Flag                | Metavar | Description                                          |
|---------------------|---------|------------------------------------------------------|
| `--title1`          | `TEXT`  | Cover title line 1                                   |
| `--title2`          | `TEXT`  | Cover title line 2                                   |
| `--subtitle`        | `TEXT`  | Cover subtitle                                       |
| `--author`          | `TEXT`  | Author line                                          |
| `--version`         | `TEXT`  | Version field (e.g. `"v2.0 DRAFT"`)                 |
| `--classification`  | `TEXT`  | Classification level (e.g. `"[RESTRICTED]"`)         |
| `--year`            | `TEXT`  | Year for the cover page                              |
| `--doc-type`        | `TEXT`  | Document type (e.g. `"Report"`, `"Assessment"`)      |
| `--doc-title`       | `TEXT`  | Page footer document title                           |
| `--doc-id`          | `TEXT`  | Document ID prefix (e.g. `"A1"`, `"Ch1"`)           |

These flags take highest priority in the metadata resolution order:

1. **CLI flags** (highest)
2. **YAML front-matter** in the Markdown file
3. **Theme defaults**
4. **Built-in defaults** (lowest)

### Theme Flags

| Flag            | Metavar | Description                                         |
|-----------------|---------|-----------------------------------------------------|
| `--theme`       | `NAME`  | Theme name to use (e.g. `mytheme`)                  |
| `--themes-dir`  | `PATH`  | Path to the directory containing theme directories  |

These flags are available on `init` and `build`.

---

## Exit Codes

| Code | Meaning                                                        |
|------|----------------------------------------------------------------|
| `0`  | Success — document built without errors                        |
| `1`  | Error — missing input file, invalid config, build failure, or missing dependencies |

---

## Environment Variables

| Variable              | Description                                                    |
|-----------------------|----------------------------------------------------------------|
| `PHOENIX_THEME`       | Default theme name (overridden by `--theme` or front-matter)   |
| `PHOENIX_THEMES_DIR`  | Path to the themes directory (overridden by `--themes-dir`)    |
| `PHOENIX_CONFIG`      | Path to the global config file (default: `~/.config/phoenix-docgen/config.yaml`) |

### Resolution Priority

**Theme name** is resolved in this order:

1. `--theme` CLI flag
2. `theme:` in YAML front-matter or combine config
3. `PHOENIX_THEME` environment variable
4. `default_theme` in the global config file
5. Auto-detect (if exactly one theme directory exists)
6. Built-in defaults (no theme)

**Themes directory** is resolved in this order:

1. `--themes-dir` CLI flag
2. `PHOENIX_THEMES_DIR` environment variable
3. `themes_dir` in the global config file
4. `themes/` relative to the installed scripts

**Global config file** is resolved in this order:

1. `PHOENIX_CONFIG` environment variable
2. Platform default: `~/.config/phoenix-docgen/config.yaml` (macOS/Linux) or `%APPDATA%\phoenix-docgen\config.yaml` (Windows)

---

## Shell Wrapper

The installed command (`phoenix-docgen` / `pdg`) is a thin shell wrapper (`phoenix-docgen.sh`) that:

1. Verifies the Python backend exists at `~/.local/share/phoenix-docgen/phoenix-docgen.py`
2. Verifies the Python virtual environment exists at `~/.local/share/phoenix-docgen/venv/`
3. Activates the virtual environment (which provides WeasyPrint and PyYAML)
4. Passes all arguments through to the Python backend

This means you never need to manually activate the virtual environment or manage Python dependencies. The wrapper handles it transparently.

If the venv is missing, the wrapper exits with an error message and instructions for recreating it:

```bash
python3 -m venv ~/.local/share/phoenix-docgen/venv
source ~/.local/share/phoenix-docgen/venv/bin/activate
pip install weasyprint pyyaml
```

The `pdg` alias is a symlink to `phoenix-docgen` created during installation, so both commands behave identically.

---

## Docker Wrapper

When using the Docker installation, the `pdg-docker` command is a thin script that translates your command into a `docker run` invocation. It automatically:

- Mounts your current working directory as the container's working directory
- Mounts your themes directory (from `PHOENIX_THEMES_DIR` or the config file)
- Passes all CLI arguments through to the containerised phoenix-docgen
- Sets file ownership correctly on Linux

The Docker wrapper supports the same subcommands and flags as the native installation. See [Docker](docker.md) for full setup and usage instructions.

You can override the Docker image with the `PDG_IMAGE` environment variable:

```bash
export PDG_IMAGE="ghcr.io/hoppers99/phoenix-docgen:v1.0.0"
```
