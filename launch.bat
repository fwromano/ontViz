@echo off
setlocal

REM Ensure we're in the project root by checking for requirements.txt
if not exist "requirements.txt" (
    echo requirements.txt not found. Please run this script from the project root.
    pause
    exit /b 1
)

REM Check if the virtual environment exists (using venv)
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Creating one...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment. Ensure you have Python 3.7+ installed.
        pause
        exit /b 1
    )
)

REM Activate the virtual environment
call venv\Scripts\activate.bat

REM Install or update dependencies
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Dependency installation failed.
    pause
    exit /b 1
)

REM Launch the Flask application in a new window
echo Starting Flask app...
start "" python app.py

REM Wait a few seconds to allow the server to start
timeout /t 3 >nul

REM Open the default web browser to the application URL
start "" "http://127.0.0.1:5000"

echo Flask app launched. Press any key to exit this window.
pause
