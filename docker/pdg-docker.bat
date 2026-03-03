@echo off
REM pdg-docker — phoenix-docgen Docker wrapper (cmd.exe)
REM Delegates to PowerShell script for full logic.
powershell -ExecutionPolicy Bypass -File "%~dp0pdg-docker.ps1" %*
