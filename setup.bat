@echo off
setlocal

REM Check if Git is installed.
where git >nul 2>&1
if errorlevel 1 (
    echo Git is not installed. Please install Git first.
    pause
    exit /b 1
)

REM Clone repository if not already present.
if not exist "ontViz\" (
    echo Cloning repository...
    git clone https://github.com/fwromano/ontViz.git
    if errorlevel 1 (
        echo Failed to clone repository.
        pause
        exit /b 1
    )
    cd ontViz
) else (
    cd ontViz
)

REM Verify that requirements.txt exists.
if not exist "requirements.txt" (
    echo requirements.txt not found. Please ensure you are in the correct repository.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist.
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment using venv...
    python -m venv venv
    if errorlevel 1 (
        echo venv failed. Trying virtualenv...
        python -m pip install --user virtualenv
        python -m virtualenv venv
        if errorlevel 1 (
            echo Failed to create a virtual environment.
            pause
            exit /b 1
        )
    )
)

REM Activate the virtual environment.
call venv\Scripts\activate.bat

REM Install dependencies.
echo Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Dependency installation failed.
    pause
    exit /b 1
)

echo Setup complete. Your application is now ready.
pause
