<#
.SYNOPSIS
    Launches the Ontology Visualization Flask server.
.DESCRIPTION
    This script activates the existing Python virtual environment,
    starts the Flask server (app.py) in a new process, and then opens
    the default web browser at http://127.0.0.1:5000.
.NOTES
    Ensure that you have already run the setup script (setup.ps1) so that the
    virtual environment and dependencies are in place.
#>

# Check if the virtual environment exists
if (-not (Test-Path ".\venv\Scripts\Activate.ps1")) {
    Write-Host "Virtual environment not found. Please run setup.ps1 first." -ForegroundColor Red
    exit 1
}

# Activate the virtual environment
Write-Host "Activating virtual environment..."
& ".\venv\Scripts\Activate.ps1"

# Start the Flask server in a new process
Write-Host "Starting Flask server..."
Start-Process "python" "app.py"

# Optional: wait a few seconds to ensure the server is up before opening the browser
Start-Sleep -Seconds 2

# Open the default web browser to the application URL
Write-Host "Opening browser at http://127.0.0.1:5000..."
Start-Process "http://127.0.0.1:5000"
