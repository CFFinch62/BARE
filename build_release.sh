#!/bin/bash
# BARE IDE — Release build (PyInstaller)
# Produces a single executable at dist/bare-ide from installer/bare_ide.spec.
# (The spec lives outside build/ deliberately — .gitignore excludes build/
# wholesale since PyInstaller writes its own intermediate output there.)

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ -d "venv" ]; then
    source venv/bin/activate
fi

if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "PyInstaller not found — installing build extras..."
    pip install -e ".[build]"
fi

echo "=== Building BARE IDE executable ==="
pyinstaller --noconfirm installer/bare_ide.spec

echo ""
echo "=== Build complete ==="
echo "Executable: dist/bare-ide"
