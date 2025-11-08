@echo off
REM Install all required Python dependencies

echo Installing Python dependencies...
echo.

pip install -r requirements.txt

echo.
echo Installation complete!
echo.
echo You can now run: update_patreon_image.bat
echo.
pause
