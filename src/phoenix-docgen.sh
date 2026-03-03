#!/bin/bash
# phoenix-docgen — branded document builder
#
# Converts markdown documents to professionally styled HTML and PDF
# using configurable themes (fonts, colours, cover, logo).
#
# Usage:
#   phoenix-docgen init document.md [--title1 TEXT] [--title2 TEXT] ...
#   phoenix-docgen init --config project.yaml [--chapters FILE ...]
#   phoenix-docgen build document.md [--pdf] [--version TEXT] ...
#   phoenix-docgen combine --config project.yaml [--pdf]
#   phoenix-docgen help [topic]
#   phoenix-docgen --help

set -euo pipefail

TOOL_DIR="$HOME/.local/share/phoenix-docgen"

# Check Python backend exists
if [[ ! -f "$TOOL_DIR/phoenix-docgen.py" ]]; then
    echo "ERROR: Python backend not found at $TOOL_DIR/phoenix-docgen.py"
    exit 1
fi

# Check venv exists
if [[ ! -f "$TOOL_DIR/venv/bin/activate" ]]; then
    echo "ERROR: Python venv not found at $TOOL_DIR/venv/"
    echo "Create it with: python3 -m venv $TOOL_DIR/venv && source $TOOL_DIR/venv/bin/activate && pip install weasyprint pyyaml"
    exit 1
fi

# Activate venv (has weasyprint, pyyaml)
source "$TOOL_DIR/venv/bin/activate"

# Run Python backend, passing all arguments through
exec python3 "$TOOL_DIR/phoenix-docgen.py" "$@"
