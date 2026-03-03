#!/bin/bash
# install.sh — phoenix-docgen development setup
#
# Creates symlinks from the repo into the installed locations so that
# changes in the repo are immediately available without re-installing.
#
# Usage:
#   ./install.sh              # Set up symlinks and venv
#   ./install.sh --uninstall  # Remove symlinks

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
TOOL_DIR="$HOME/.local/share/phoenix-docgen"
BIN_DIR="$HOME/.local/bin"
CONFIG_DIR="$HOME/.config/phoenix-docgen"

# ── Uninstall ────────────────────────────────────────────────────────

if [[ "${1:-}" == "--uninstall" ]]; then
    echo "Removing phoenix-docgen symlinks..."
    rm -f "$BIN_DIR/phoenix-docgen" "$BIN_DIR/pdg"
    rm -rf "$TOOL_DIR"
    echo "Done. Config at $CONFIG_DIR left intact."
    exit 0
fi

# ── Install ──────────────────────────────────────────────────────────

echo "phoenix-docgen — development install"
echo "  Repo:    $REPO_DIR"
echo "  Tool:    $TOOL_DIR"
echo "  Bin:     $BIN_DIR"
echo

# Create directories
mkdir -p "$TOOL_DIR" "$BIN_DIR" "$CONFIG_DIR"

# Symlink Python source files
echo "Linking source files..."
for f in phoenix-docgen.py shared_styles.py cover_utils.py help_topics.py theme.py; do
    ln -sf "$REPO_DIR/src/$f" "$TOOL_DIR/$f"
    echo "  $f → $TOOL_DIR/$f"
done

# Symlink themes directory
if [[ -d "$REPO_DIR/themes" ]]; then
    ln -sfn "$REPO_DIR/themes" "$TOOL_DIR/themes"
    echo "  themes/ → $TOOL_DIR/themes"
fi

# Symlink shell wrapper + short alias
ln -sf "$REPO_DIR/src/phoenix-docgen.sh" "$BIN_DIR/phoenix-docgen"
ln -sf phoenix-docgen "$BIN_DIR/pdg"
chmod +x "$BIN_DIR/phoenix-docgen"
echo "  phoenix-docgen → $BIN_DIR/phoenix-docgen"
echo "  pdg            → $BIN_DIR/pdg (alias)"

# Create venv if it doesn't exist
if [[ ! -f "$TOOL_DIR/venv/bin/activate" ]]; then
    echo
    echo "Creating Python venv..."
    python3 -m venv "$TOOL_DIR/venv"
    source "$TOOL_DIR/venv/bin/activate"
    pip install --quiet weasyprint pyyaml
    echo "  venv created with weasyprint and pyyaml"
else
    echo "  venv already exists"
fi

# Create default config if it doesn't exist
if [[ ! -f "$CONFIG_DIR/config.yaml" ]]; then
    cat > "$CONFIG_DIR/config.yaml" << 'YAML'
# phoenix-docgen global configuration
#
# themes_dir: ~/themes/phoenix-docgen    # Where to find theme directories
# default_theme: mytheme                 # Default theme when none specified
YAML
    echo "  config.yaml created at $CONFIG_DIR/config.yaml"
else
    echo "  config.yaml already exists"
fi

echo
echo "Done. Run 'phoenix-docgen --help' or 'pdg --help' to verify."
