# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller build spec for the standalone BARE CLI interpreter.

Build with (from the project root, inside the dev venv):
    pyinstaller installer/bare_cli.spec

Produces a single-file console executable: dist/bare (dist/bare.exe on
Windows). Install it with:

    cp dist/bare ~/.local/bin/bare

This is the runtime the VS Code extension drives (editors/vscode). It is
also what MyCode launches. The IDE remains the primary way to run BARE
programs -- this binary exists so an editor that is not the BARE IDE can
run a .bare file without bundling PyQt6.

Deliberately console=True (unlike bare_ide.spec): the whole point of this
build is stdout, stderr and a meaningful exit code.

Only bare_core is packaged, never bare_ide, so the binary carries no Qt
dependency at all -- bare_core imports no PyQt.
"""

from pathlib import Path

ROOT = Path(SPECPATH).parent  # SPECPATH is injected by PyInstaller at build time
SRC = ROOT / "src"

a = Analysis(
    [str(ROOT / "bare_cli.py")],
    pathex=[str(SRC)],
    binaries=[],
    # No datas: the CLI reads only the .bare file it is handed. The IDE
    # bundles icons/examples/docs because it presents them; this does not.
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # Keep Qt out of a console binary that has no use for it.
    excludes=["PyQt6", "bare_ide"],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="bare",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
