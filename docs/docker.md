# Docker

phoenix-docgen is available as a Docker image, providing a self-contained environment with Python, pandoc, WeasyPrint, and all native dependencies pre-installed. This is the recommended installation method for Windows users and is available as an alternative on any platform.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) (Windows/macOS) or [Docker Engine](https://docs.docker.com/engine/install/) (Linux)

No other dependencies are needed — Python, pandoc, WeasyPrint, and all native libraries are bundled in the image.

## Quick Start

### 1. Pull the Image

```bash
docker pull ghcr.io/hoppers99/phoenix-docgen:latest
```

### 2. Install the Wrapper Script

The wrapper script translates normal `pdg-docker` commands into `docker run` invocations, automatically mounting your working directory and themes.

**macOS / Linux:**

```bash
cp docker/pdg-docker.sh ~/.local/bin/pdg-docker
chmod +x ~/.local/bin/pdg-docker
```

**Windows (PowerShell):**

Copy `docker\pdg-docker.ps1` and `docker\pdg-docker.bat` to a directory on your `PATH` (e.g. `C:\Tools\`).

### 3. Configure Your Themes Directory

Set the `PHOENIX_THEMES_DIR` environment variable to point at your themes:

**macOS / Linux:**

```bash
export PHOENIX_THEMES_DIR="$HOME/themes/phoenix-docgen"
```

Add this to your shell profile (`~/.zshrc`, `~/.bashrc`, etc.) to make it permanent.

**Windows (PowerShell):**

```powershell
[Environment]::SetEnvironmentVariable("PHOENIX_THEMES_DIR",
    "$env:USERPROFILE\themes\phoenix-docgen", "User")
```

### 4. Verify

```bash
pdg-docker --help
```

You should see the phoenix-docgen usage summary.

---

## Usage

The wrapper accepts the same commands and flags as the native `pdg` command:

```bash
# Scaffold a new document
pdg-docker init report.md --title1 "MY" --title2 "REPORT"

# Build to HTML + PDF
pdg-docker build report.md --pdf

# Build with a specific theme
pdg-docker build report.md --theme mytheme --pdf

# Multi-chapter combine
pdg-docker combine --config project.yaml --pdf

# Help
pdg-docker help frontmatter
```

---

## How It Works

The wrapper script performs the following steps:

1. **Checks Docker is available** and the daemon is running
2. **Discovers your themes directory** from `PHOENIX_THEMES_DIR` or the global config file
3. **Mounts your current working directory** as `/work` inside the container
4. **Mounts your themes directory** as `/themes` (read-only)
5. **Optionally mounts your config file** if `~/.config/phoenix-docgen/config.yaml` exists
6. **Passes all arguments through** to the containerised phoenix-docgen

Output files (HTML and PDF) are written to your working directory — they appear alongside your Markdown source files, just as with the native installation.

### Manual `docker run`

If you prefer not to use the wrapper, you can invoke Docker directly:

```bash
docker run --rm \
  -v "$(pwd):/work" \
  -v "$PHOENIX_THEMES_DIR:/themes:ro" \
  ghcr.io/hoppers99/phoenix-docgen:latest \
  build report.md --pdf
```

On Linux, add `-u "$(id -u):$(id -g)"` to ensure output files are owned by your user rather than root:

```bash
docker run --rm \
  -v "$(pwd):/work" \
  -v "$PHOENIX_THEMES_DIR:/themes:ro" \
  -u "$(id -u):$(id -g)" \
  ghcr.io/hoppers99/phoenix-docgen:latest \
  build report.md --pdf
```

---

## Configuration

### Environment Variables

The wrapper respects these environment variables:

| Variable               | Description                                                     |
|------------------------|-----------------------------------------------------------------|
| `PHOENIX_THEMES_DIR`   | Path to the directory containing theme directories              |
| `PHOENIX_THEME`        | Default theme name (passed through to the container)            |
| `PHOENIX_CONFIG`       | Path to the global config file                                  |
| `PDG_IMAGE`            | Override the Docker image (default: `ghcr.io/hoppers99/phoenix-docgen:latest`) |

### Global Config File

If `~/.config/phoenix-docgen/config.yaml` (or `%APPDATA%\phoenix-docgen\config.yaml` on Windows) exists, the wrapper:

- Reads `themes_dir` from it to discover themes (if `PHOENIX_THEMES_DIR` is not set)
- Mounts the config file into the container at `/config/config.yaml`

### Image Versioning

Pin to a specific version by setting `PDG_IMAGE`:

```bash
export PDG_IMAGE="ghcr.io/hoppers99/phoenix-docgen:v1.0.0"
```

---

## Limitations

When running via Docker, there are a few differences from the native installation:

1. **Use `PHOENIX_THEMES_DIR` instead of `--themes-dir`** — the `--themes-dir` CLI flag specifies a path that must exist inside the container. The environment variable is handled by the wrapper and correctly translated to a volume mount.

2. **Use relative paths in combine configs** — chapter file paths in your YAML config should be relative to the config file (e.g. `chapters/intro.md`), not absolute paths. Absolute paths would reference locations inside the container.

3. **Output goes to the working directory** — files are written to the directory where you run the command, which is mounted into the container.

---

## Building the Image Locally

For contributors or custom builds:

```bash
cd docker
make build
```

This builds the image from the repo root using the `Dockerfile`. The image is tagged with both the current git version and `latest`.

For multi-architecture builds (amd64 + arm64):

```bash
cd docker
make build-multiarch
```

This uses Docker Buildx to build and push images for both Intel/AMD and Apple Silicon / ARM platforms.

---

## Troubleshooting

### "Docker is not installed or not on PATH"

Install [Docker Desktop](https://www.docker.com/products/docker-desktop) (Windows/macOS) or Docker Engine (Linux). On macOS with Homebrew: `brew install --cask docker`.

### "Docker daemon is not running"

Start Docker Desktop. On Linux: `sudo systemctl start docker`.

### Output files are owned by root (Linux)

The wrapper automatically adds `-u "$(id -u):$(id -g)"` on Linux. If running `docker run` manually, include this flag.

### Fonts render differently

The Docker image uses Debian's system fonts as the base. Theme fonts (specified in `theme.yaml`) are embedded as base64 data URIs, so they render identically to the native installation. If you see differences, ensure your theme includes explicit font files rather than relying on system fonts.

### Image is slow on first run

The first `docker run` pulls the image if it has not been downloaded yet. Subsequent runs start in under a second. To pre-pull: `docker pull ghcr.io/hoppers99/phoenix-docgen:latest`.

---

## Native vs Docker

| Aspect                 | Native (`pdg`)              | Docker (`pdg-docker`)                    |
|------------------------|-----------------------------|------------------------------------------|
| Setup effort           | `./install.sh`              | Install Docker + pull image              |
| macOS                  | Recommended (faster)        | Available by choice                      |
| Windows                | Possible but fiddly         | Recommended                              |
| Linux                  | Works well                  | Works well                               |
| WeasyPrint deps        | Homebrew / apt              | Bundled in image                         |
| Pandoc                 | Homebrew / apt              | Bundled in image                         |
| Startup time           | Instant                     | ~0.5s container overhead                 |
| Docker Desktop needed  | No                          | Yes (Windows/macOS)                      |
| Output consistency     | Platform fonts may vary     | Identical across platforms               |
