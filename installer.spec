# -*- mode: python ; coding: utf-8 -*-
import os

# dynamic name passed from CI/CD
artifact_name = os.getenv("PYI_NAME", "pyi_name_not_set")

a = Analysis(
    ["runme.py"],
    pathex=[],
    binaries=[],
    datas=[("alembic.ini", "."), ("alembic", "alembic")],
    hiddenimports=["holidays.countries"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=artifact_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=["ui\\clock.png"],
)
