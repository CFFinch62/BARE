#!/bin/bash
# BARE IDE — Development environment setup
# Creates a virtual environment and installs dependencies.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== BARE Development Environment Setup ==="

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "Virtual environment created."
else
    echo "Virtual environment already exists."
fi

# Activate and install
echo "Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev,ide]"

echo ""
echo "=== Setup complete! ==="
echo "To activate the environment:  source venv/bin/activate"
echo "To run tests:                 python -m pytest tests/ -v"
echo "To run the IDE:               python -m bare_ide.main"
echo "To run a .bare file (dev):    python -m bare_core myfile.bare"
