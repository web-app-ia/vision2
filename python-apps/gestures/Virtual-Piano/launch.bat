@echo off
echo ====================================
echo   Virtual Piano (Keyboard Only)
echo ====================================
echo.

cd /d "%~dp0"

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

echo Installing required packages...
pip install pygame pynput

echo.
echo Starting Virtual Piano...
echo Use keys 1-8 (left hand) and Q-I (right hand)
echo Press ESC to exit
echo.

python main.py

pause
