# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller build spec for BARE IDE.

Build with (from the project root, inside the dev venv):
    pyinstaller installer/bare_ide.spec

Lives in installer/ rather than build/ deliberately: PyInstaller writes
its own intermediate output to ./build by default, and .gitignore already
excludes build/ wholesale for that reason — putting the spec there too
would make it invisible to git.

Produces a single-file executable: dist/bare-ide (dist/bare-ide.exe on
Windows). BARE is IDE-locked — there is no separate bare_core CLI binary
to package; this is the one and only distributable artifact.

Icon note: icons/ currently only has SVGs. PyInstaller needs a .ico for
Windows or .icns for macOS to brand the executable/app bundle — add one
and set `icon=` in the EXE() call below once those assets exist. Linux
builds don't use this field at all, so it's not blocking today.
"""

from pathlib import Path

ROOT = Path(SPECPATH).parent  # SPECPATH is injected by PyInstaller at build time
SRC = ROOT / "src"

a = Analysis(
    [str(SRC / "bare_ide" / "main.py")],
    pathex=[str(SRC)],
    binaries=[],
    datas=[
        (str(ROOT / "icons"), "icons"),
        (str(ROOT / "examples"), "examples"),
        (str(ROOT / "docs"), "docs"),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name="bare-ide",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
