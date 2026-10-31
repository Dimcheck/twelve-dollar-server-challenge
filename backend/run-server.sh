#!/bin/bash
# Starts the backend server with virtualenv setup and environment variables
set -euo pipefail

cd "$(dirname "$0")"

# Create virtualenv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Installing dependencies..."
    venv/bin/pip install --disable-pip-version-check --no-input --quiet -r requirements.txt
fi

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Start the server
venv/bin/python -m uvicorn main:app
