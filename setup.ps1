<#
.SYNOPSIS
   Sets up the Ontology Visualization project by cloning the repository (if needed),
   creating a virtual environment, installing dependencies, and launching the Flask server.

.DESCRIPTION
   This script is intended to be run in PowerShell. It will:
     - Verify Git is installed.
     - Clone the repository if the "ontViz" folder does not exist,
       or update it if it does.
     - Create and activate a Python virtual environment.
     - Install required packages from requirements.txt.
     - Start the Flask server in a new process and open the default web browser.

.NOTES
   Ensure your PowerShell execution policy permits running scripts (for example, run:
   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser).
#>

# Check if Git is installed
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "Git is not installed. Please install Git first." -ForegroundColor Red
    exit 1
}

# Define repository folder name (adjust if necessary)
$repoFolder = "ontViz"

# If the repository folder does not exist, clone the repository; otherwise, update it.
if (-not (Test-Path $repoFolder)) {
    Write-Host "Cloning repository..."
    git clone https://github.com/fwromano/ontViz.git
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to clone repository." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Repository already exists. Updating repository..."
    Push-Location $repoFolder
    git pull
    Pop-Location
}

# Change to repository directory
Set-Location $repoFolder

# Create virtual environment if not already present
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to create virtual environment." -ForegroundColor Red
        exit 1
    }
}

# Activate the virtual environment
Write-Host "Activating virtual environment..."
$activateScript = ".\venv\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
} else {
    Write-Host "Activation script not found. Ensure you're running PowerShell on Windows." -ForegroundColor Red
    exit 1
}

# (Optional) Upgrade pip
Write-Host "Upgrading pip..."
pip install --upgrade pip

# Install dependencies from requirements.txt
Write-Host "Installing dependencies..."
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install dependencies." -ForegroundColor Red
    exit 1
}

# Start the Flask server in a new window
Write-Host "Starting Flask server..."
Start-Process "python" "app.py"

# Open the default browser to the application URL
Write-Host "Flask server started. Opening browser..."
Start-Process "http://127.0.0.1:5000"
