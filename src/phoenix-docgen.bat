@echo off
REM phoenix-docgen — branded document builder (Windows)
REM
REM Converts markdown documents to professionally styled HTML and PDF
REM using configurable themes (fonts, colours, cover, logo).

set TOOL_DIR=%LOCALAPPDATA%\phoenix-docgen

REM Check Python backend exists
if not exist "%TOOL_DIR%\phoenix-docgen.py" (
    echo ERROR: Python backend not found at %TOOL_DIR%\phoenix-docgen.py
    exit /b 1
)

REM Check venv exists
if not exist "%TOOL_DIR%\venv\Scripts\activate.bat" (
    echo ERROR: Python venv not found at %TOOL_DIR%\venv\
    echo Create it with: python -m venv %TOOL_DIR%\venv ^&^& %TOOL_DIR%\venv\Scripts\activate ^&^& pip install weasyprint pyyaml
    exit /b 1
)

REM Activate venv and run Python backend
call "%TOOL_DIR%\venv\Scripts\activate.bat"
python "%TOOL_DIR%\phoenix-docgen.py" %*
