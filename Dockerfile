# phoenix-docgen — branded document builder
#
# Converts markdown documents to professionally styled HTML and PDF
# using configurable themes (fonts, colours, cover, logo).
#
# Usage:
#   docker build -t phoenix-docgen .
#   docker run --rm -v "$(pwd):/work" -v "$THEMES:/themes:ro" phoenix-docgen build doc.md --pdf
#
# Mount points:
#   /work    — working directory (input markdown, output HTML/PDF)
#   /themes  — themes directory (read-only)

# ── Build arguments ─────────────────────────────────────────────────
ARG PYTHON_VERSION=3.12
ARG PANDOC_VERSION=3.6.4

# ── Base image ───────────────────────────────────────────────────────
FROM python:${PYTHON_VERSION}-slim

LABEL org.opencontainers.image.source="https://github.com/hoppers99/phoenix-docgen"
LABEL org.opencontainers.image.description="phoenix-docgen — branded document builder"
LABEL org.opencontainers.image.licenses="MIT"

# ── System dependencies ─────────────────────────────────────────────
# WeasyPrint requires Cairo, Pango, GDK-Pixbuf, and shared-mime-info.
# wget is used to fetch pandoc and then removed.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libcairo2 \
        libpango-1.0-0 \
        libpangocairo-1.0-0 \
        libgdk-pixbuf-2.0-0 \
        libffi-dev \
        shared-mime-info \
        wget \
    && rm -rf /var/lib/apt/lists/*

# ── Install pandoc from GitHub release ───────────────────────────────
ARG PANDOC_VERSION
ARG TARGETARCH
RUN ARCH=$(case ${TARGETARCH} in arm64) echo "arm64";; *) echo "amd64";; esac) \
    && wget -q "https://github.com/jgm/pandoc/releases/download/${PANDOC_VERSION}/pandoc-${PANDOC_VERSION}-1-${ARCH}.deb" \
       -O /tmp/pandoc.deb \
    && dpkg -i /tmp/pandoc.deb \
    && rm /tmp/pandoc.deb \
    && apt-get purge -y wget \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# ── Python dependencies ─────────────────────────────────────────────
RUN pip install --no-cache-dir weasyprint pyyaml

# ── Application source ──────────────────────────────────────────────
COPY src/phoenix-docgen.py src/shared_styles.py src/cover_utils.py \
     src/help_topics.py src/theme.py \
     /app/

# ── Runtime configuration ───────────────────────────────────────────
# Themes are mounted at /themes by the wrapper scripts
ENV PHOENIX_THEMES_DIR=/themes
ENV PYTHONPATH=/app

# Working directory — wrappers mount the host CWD here
WORKDIR /work

ENTRYPOINT ["python3", "/app/phoenix-docgen.py"]
CMD ["--help"]
