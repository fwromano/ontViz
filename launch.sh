#!/bin/bash
set -e

# Ensure we're in the repo root by checking for requirements.txt.
if [ ! -f "requirements.txt" ]; then
  echo "requirements.txt not found – are you in the ontViz repository?"
  exit 1
fi

# Function to check if a command works.
function command_exists() {
  command -v "$1" &> /dev/null
}

# Try to create a virtual environment.
if [ ! -d "venv" ]; then
  echo "No virtual environment found. Attempting to create one..."
  if python3 -m venv --help > /dev/null 2>&1; then
    echo "Using built-in venv..."
    python3 -m venv venv
  elif python3 -m virtualenv --help > /dev/null 2>&1; then
    echo "Using virtualenv..."
    python3 -m virtualenv venv
  elif command_exists pipenv; then
    echo "Using pipenv..."
    pipenv --python python3
    pipenv install -r requirements.txt
    echo "Launching Flask app with pipenv..."
    pipenv run python app.py
    exit 0
  else
    echo "No virtual environment tool found. Installing virtualenv via pip..."
    python3 -m pip install --user virtualenv
    python3 -m virtualenv venv
  fi
fi

# Activate the virtual environment.
if [ -f "venv/bin/activate" ]; then
  source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
  source venv/Scripts/activate
else
  echo "Unable to locate the virtual environment activation script."
  exit 1
fi

# Install or update dependencies.
pip install -r requirements.txt

# Launch the Flask application.
echo "Starting Flask app..."
python app.py &
FLASK_PID=$!

# Give the server a moment to start.
sleep 2

# Open the default web browser.
python -c "import webbrowser; webbrowser.open('http://127.0.0.1:5000')"

# Wait for the Flask server to finish.
wait $FLASK_PID
