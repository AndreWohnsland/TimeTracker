# -*- mode: python ; coding: utf-8 -*-
import os
from pathlib import Path

# dynamic name passed from CI/CD
artifact_name = os.getenv("PYI_NAME", "pyi_name_not_set")
icon_path = str((Path("stempeluhr") / "ui" / "clock.png").resolve())

a = Analysis(
    ["runme.py"],
    pathex=[],
    binaries=[],
    # alembic loads migrations from a real directory (MIGRATIONS_PATH), so ship them as data
    datas=[("stempeluhr/migrations", "stempeluhr/migrations")],
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
    icon=[icon_path],
)

app = BUNDLE(
    exe,
    name=f"{artifact_name}.app",
    icon=icon_path,
    bundle_identifier=None,
)
