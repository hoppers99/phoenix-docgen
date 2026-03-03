---
description: Build branded PDF documents from markdown using configurable themes (init, build, combine)
---

You are executing the `/phoenix-docgen` command to build branded documents.

**Tool**: `phoenix-docgen` (on PATH via `~/.local/bin/`)

**Task**: Parse the user's arguments and execute the appropriate phoenix-docgen subcommand.

**Steps**:

1. Determine the subcommand from the user's input:
   - If they want to **create/scaffold** a new document → use `init`
   - If they want to **build** a single markdown file → use `build`
   - If they want to **combine** multiple chapters → use `combine`
   - If no arguments or just "help" → run with `--help`

2. Execute the command:
   ```bash
   phoenix-docgen <subcommand> <args>
   ```

3. Present the results to the user.

**Example invocations**:
- `/phoenix-docgen init report.md --title1 "AI" --title2 "STRATEGY"` → scaffold a new document
- `/phoenix-docgen build report.md --pdf` → build markdown to HTML + PDF
- `/phoenix-docgen build report.md --theme mytheme --pdf` → build with a specific theme
- `/phoenix-docgen build report.md --version "v2.0 FINAL" --pdf` → build with version override
- `/phoenix-docgen combine --config project.yaml --pdf` → build multi-chapter document
- `/phoenix-docgen combine --config project.yaml --theme mytheme --pdf` → combine with theme
- `/phoenix-docgen help` → show help
- `/phoenix-docgen help branding` → show theme system documentation

**Important notes**:
- `phoenix-docgen` is on PATH — no full path needed
- The wrapper handles venv activation automatically
- For `build`, the markdown file should have YAML front-matter (use `init` to scaffold one)
- For `combine`, a YAML config file defining chapters is required (use `init --config` to scaffold one)
- `--pdf` flag triggers PDF generation (otherwise HTML only)
- `--theme NAME` selects a specific theme (overrides front-matter and config file)
- `--themes-dir PATH` overrides the themes directory location
- All metadata can be overridden via CLI flags (`--version`, `--title1`, `--title2`, etc.)
- Themes are configured in `~/.config/phoenix-docgen/config.yaml`

Execute the command now with the user's arguments.
