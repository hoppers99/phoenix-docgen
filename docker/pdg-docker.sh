#!/bin/bash
# pdg-docker — phoenix-docgen Docker wrapper
#
# Translates pdg-docker commands into docker run invocations,
# automatically mounting the working directory and themes.
#
# Install:
#   cp docker/pdg-docker.sh ~/.local/bin/pdg-docker
#   chmod +x ~/.local/bin/pdg-docker
#
# Usage:
#   pdg-docker build report.md --pdf
#   pdg-docker combine --config project.yaml --pdf
#   pdg-docker init document.md --title1 "My Report"
#   pdg-docker help frontmatter

set -euo pipefail

IMAGE="${PDG_IMAGE:-ghcr.io/hoppers99/phoenix-docgen:latest}"

# ── Check Docker is available ────────────────────────────────────────

if ! command -v docker &>/dev/null; then
    echo "ERROR: Docker is not installed or not on PATH." >&2
    echo "Install Docker Desktop: https://www.docker.com/products/docker-desktop" >&2
    exit 1
fi

if ! docker info &>/dev/null 2>&1; then
    echo "ERROR: Docker daemon is not running." >&2
    echo "Start Docker Desktop and try again." >&2
    exit 1
fi

# ── Determine themes directory ───────────────────────────────────────
# Priority: PHOENIX_THEMES_DIR env → config file → skip

THEMES_DIR="${PHOENIX_THEMES_DIR:-}"

if [[ -z "$THEMES_DIR" ]]; then
    CONFIG_FILE="${PHOENIX_CONFIG:-$HOME/.config/phoenix-docgen/config.yaml}"
    if [[ -f "$CONFIG_FILE" ]]; then
        THEMES_DIR=$(grep -E '^\s*themes_dir:' "$CONFIG_FILE" 2>/dev/null \
                     | sed 's/.*themes_dir:\s*//' | sed 's/#.*//' | xargs) || true
        THEMES_DIR="${THEMES_DIR/#\~/$HOME}"
    fi
fi

# ── Build docker run command ─────────────────────────────────────────

DOCKER_ARGS=(
    run --rm
    -v "$(pwd):/work"
)

# Mount themes directory if it exists
if [[ -n "$THEMES_DIR" && -d "$THEMES_DIR" ]]; then
    DOCKER_ARGS+=(-v "$THEMES_DIR:/themes:ro")
fi

# Pass through PHOENIX_THEME env var if set
if [[ -n "${PHOENIX_THEME:-}" ]]; then
    DOCKER_ARGS+=(-e "PHOENIX_THEME=$PHOENIX_THEME")
fi

# Mount config file if it exists
CONFIG_FILE="${PHOENIX_CONFIG:-$HOME/.config/phoenix-docgen/config.yaml}"
if [[ -f "$CONFIG_FILE" ]]; then
    DOCKER_ARGS+=(-v "$CONFIG_FILE:/config/config.yaml:ro")
    DOCKER_ARGS+=(-e "PHOENIX_CONFIG=/config/config.yaml")
fi

# Set UID/GID so output files are owned by the current user (Linux)
if [[ "$(uname)" != "Darwin" ]]; then
    DOCKER_ARGS+=(-u "$(id -u):$(id -g)")
fi

DOCKER_ARGS+=("$IMAGE")

# Pass all arguments through to phoenix-docgen
exec docker "${DOCKER_ARGS[@]}" "$@"
