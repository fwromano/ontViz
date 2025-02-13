#!/bin/bash
set -e

# Ensure python3 is available.
if ! command -v python3 &> /dev/null; then
  echo "python3 not found. Please install Python 3.7+."
  exit 1
fi

# Function to check if "python3 -m venv" works.
function check_venv() {
  python3 -m venv --help > /dev/null 2>&1
}

# Try venv, virtualenv, then pipenv.
if check_venv; then
  ENV_METHOD="venv"
  VENV_CMD="python3 -m venv"
elif python3 -m virtualenv --help > /dev/null 2>&1; then
  ENV_METHOD="virtualenv"
  VENV_CMD="python3 -m virtualenv"
elif pipenv --version > /dev/null 2>&1; then
  ENV_METHOD="pipenv"
else
  echo "No virtual environment tool found. Attempting to install virtualenv via pip..."
  if ! python3 -m pip --version > /dev/null 2>&1; then
    echo "pip not installed. Please install pip first."
    exit 1
  fi
  python3 -m pip install --user virtualenv
  if python3 -m virtualenv --help > /dev/null 2>&1; then
    ENV_METHOD="virtualenv"
    VENV_CMD="python3 -m virtualenv"
  else
    echo "Failed to install virtualenv. Please install venv, virtualenv, or pipenv manually."
    exit 1
  fi
fi

echo "Using virtual environment method: $ENV_METHOD"

# Clone repository if not already present.
if [ ! -d "ontViz" ]; then
  git clone https://github.com/fwromano/ontViz.git
  cd ontViz
else
  cd ontViz
fi

if [ "$ENV_METHOD" == "pipenv" ]; then
  # For pipenv, create Pipfile if needed and install dependencies.
  if [ ! -f "Pipfile" ]; then
    echo "Creating Pipfile with pipenv..."
    pipenv --python python3
  fi
  echo "Installing dependencies using pipenv..."
  pipenv install -r requirements.txt
  echo "Starting Flask app with pipenv..."
  pipenv run python app.py &
  FLASK_PID=$!
else
  # For venv or virtualenv.
  if [ ! -d "venv" ]; then
    echo "Creating virtual environment using: $VENV_CMD venv"
    $VENV_CMD venv
  fi

  # Activate the virtual environment.
  if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
  elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
  else
    echo "Unable to locate virtual environment activation script."
    exit 1
  fi

  echo "Installing dependencies..."
  pip install -r requirements.txt

  echo "Starting Flask app..."
  python app.py &
  FLASK_PID=$!
fi

# Allow the server time to start.
sleep 2

# Open the default web browser to the app.
python -c "import webbrowser; webbrowser.open('http://127.0.0.1:5000')"

# Wait for the Flask server process to finish.
wait $FLASK_PID
