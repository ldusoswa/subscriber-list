@echo off
REM Batch file to run the complete Patreon image update workflow

echo Starting Patreon Image Update...
echo.

cd /d "%~dp0.."
python scripts\update_patreon_image.py

echo.
echo Press any key to exit...
pause >nul
