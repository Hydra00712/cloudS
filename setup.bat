@echo off
REM Clean way to run Azure setup via Python
REM This avoids PowerShell encoding issues

cd /d "%~dp0"

echo.
echo ================================================================================
echo AZURE SETUP - Using Python SDK
echo ================================================================================
echo.

REM Use py launcher (Windows Python Launcher)
where py >nul 2>&1
if %errorlevel% equ 0 (
    echo Found Python launcher. Installing required packages...
    py -m pip install -q azure-identity azure-mgmt-resource azure-mgmt-storage
    
    echo.
    echo Running setup script...
    py setup_simple.py
    pause
) else (
    echo ERROR: Python launcher not found in PATH
    echo.
    echo Please ensure Python 3.9+ is installed
    pause
    exit /b 1
)
