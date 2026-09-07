#!/bin/bash
# BARE CLI — Release build (PyInstaller)
# Produces a single console executable at dist/bare from installer/bare_cli.spec.
#
# This is the standalone runtime: it takes a .bare file, runs it, and reports
# errors on stderr with a meaningful exit code. It is what the VS Code
# extension (editors/vscode) drives, and what MyCode launches. The BARE IDE
# remains the primary way to run BARE programs; this binary exists so an editor
# that is not the BARE IDE can run a .bare file without bundling PyQt6.
#
# Install it with:
#     cp dist/bare ~/.local/bin/bare

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

echo "=== Building BARE CLI executable ==="
pyinstaller --noconfirm installer/bare_cli.spec

echo ""
echo "=== Build complete ==="
echo "Executable: dist/bare"
echo "Install with: cp dist/bare ~/.local/bin/bare"
