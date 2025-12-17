@echo off
REM Complete Azure Setup
cd /d "%~dp0"

echo.
echo ================================================================================
echo COMPLETE AZURE SETUP - All Resources
echo ================================================================================
echo.

py -m pip install -q azure-identity azure-mgmt-resource azure-mgmt-storage azure-mgmt-sql azure-mgmt-keyvault

py setup_full.py
pause
