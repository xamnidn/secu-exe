# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller build spec for SECU Password Generator v1.3.0

Build with:
    pyinstaller build.spec

Or via auto-py-to-exe:
    1. Open auto-py-to-exe
    2. Point Script Location to main.py
    3. Under "Hidden Imports" add:
       - argon2
       - argon2.low_level
       - _argon2_cffi_bindings
    4. Under "Additional Files", add:
       - Source: (path to SECU-Exe folder)
       - Destination: .
    5. Set "One File" = False (One Directory mode)
    6. Set "Console Window" = False
    7. Convert
"""

import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_all

# ── Force argon2-cffi native extension to be bundled ──────────────────────
# argon2-cffi ships a C extension (_argon2_cffi_bindings.pyd/.so) that
# PyInstaller does NOT detect automatically. Without this, the exe will
# fail with: "please install argon2-cffi".
try:
    import argon2
    ARGON2_DATA, ARGON2_BINS, ARGON2_HIDDEN = collect_all("argon2")
except ImportError:
    ARGON2_DATA = ARGON2_BINS = ARGON2_HIDDEN = []

a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=ARGON2_BINS,          # native .pyd/.so files
    datas=ARGON2_DATA,             # data files
    hiddenimports=ARGON2_HIDDEN + [
        "_argon2_cffi_bindings",   # C extension (argon2-cffi 25.x)
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "tkinter.test",
        "unittest",
        "pytest",
        "email",
        "http",
        "xml",
        "xmlrpc",
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="secu",
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
    icon="secu.ico",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="secu",
)
