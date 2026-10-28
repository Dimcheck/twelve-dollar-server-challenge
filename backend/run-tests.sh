#!/bin/bash
# Runs the pytest suite with virtualenv setup & environment variables
set -euo pipefail

cd "$(dirname "$0")"

# Create virtualenv if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    exec python3 -m venv venv
    echo "Installing dependencies..."
    exec venv/bin/pip install --disable-pip-version-check --no-input --quiet -r requirements.txt
fi

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Start the pytest suite
exec venv/bin/python -m pytest