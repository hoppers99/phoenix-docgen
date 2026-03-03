# pdg-docker — phoenix-docgen Docker wrapper (PowerShell)
#
# Translates pdg-docker commands into docker run invocations,
# automatically mounting the working directory and themes.
#
# Install:
#   Copy pdg-docker.ps1 and pdg-docker.bat to a directory on your PATH.
#
# Usage:
#   pdg-docker build report.md --pdf
#   pdg-docker combine --config project.yaml --pdf
#   pdg-docker init document.md --title1 "My Report"
#   pdg-docker help frontmatter

$ErrorActionPreference = "Stop"

$Image = if ($env:PDG_IMAGE) { $env:PDG_IMAGE } else { "ghcr.io/hoppers99/phoenix-docgen:latest" }

# ── Check Docker is available ────────────────────────────────────────

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Error "Docker is not installed or not on PATH. Install Docker Desktop: https://www.docker.com/products/docker-desktop"
    exit 1
}

try {
    $null = docker info 2>&1
} catch {
    Write-Error "Docker daemon is not running. Start Docker Desktop and try again."
    exit 1
}

# ── Determine themes directory ───────────────────────────────────────
# Priority: PHOENIX_THEMES_DIR env > config file > skip

$ThemesDir = $env:PHOENIX_THEMES_DIR

if (-not $ThemesDir) {
    $ConfigFile = if ($env:PHOENIX_CONFIG) { $env:PHOENIX_CONFIG }
                  else { "$env:APPDATA\phoenix-docgen\config.yaml" }
    if (Test-Path $ConfigFile -ErrorAction SilentlyContinue) {
        $line = Select-String -Path $ConfigFile -Pattern '^\s*themes_dir:' |
                Select-Object -First 1
        if ($line) {
            $ThemesDir = ($line.Line -replace '.*themes_dir:\s*', '' -replace '#.*', '').Trim()
            $ThemesDir = $ThemesDir -replace '^~', $env:USERPROFILE
        }
    }
}

# ── Build docker run command ─────────────────────────────────────────

$DockerArgs = @("run", "--rm")

# Mount current working directory
$Cwd = (Get-Location).Path
$DockerArgs += @("-v", "${Cwd}:/work")

# Mount themes directory if it exists
if ($ThemesDir -and (Test-Path $ThemesDir -ErrorAction SilentlyContinue)) {
    $DockerArgs += @("-v", "${ThemesDir}:/themes:ro")
}

# Pass through PHOENIX_THEME env var if set
if ($env:PHOENIX_THEME) {
    $DockerArgs += @("-e", "PHOENIX_THEME=$($env:PHOENIX_THEME)")
}

# Mount config file if it exists
$ConfigPath = if ($env:PHOENIX_CONFIG) { $env:PHOENIX_CONFIG }
              else { "$env:APPDATA\phoenix-docgen\config.yaml" }
if (Test-Path $ConfigPath -ErrorAction SilentlyContinue) {
    $DockerArgs += @("-v", "${ConfigPath}:/config/config.yaml:ro")
    $DockerArgs += @("-e", "PHOENIX_CONFIG=/config/config.yaml")
}

$DockerArgs += $Image

# Pass all user arguments through to phoenix-docgen
$DockerArgs += $args

& docker @DockerArgs
exit $LASTEXITCODE
