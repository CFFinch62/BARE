#!/bin/bash
# BARE IDE — Development launcher
# Runs the IDE from source (activates venv if it exists).

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ -d "venv" ]; then
    source venv/bin/activate
fi

PYTHONPATH=src python3 -m bare_ide.main "$@"
