# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.win32.versioninfo import (
    FixedFileInfo,
    StringFileInfo,
    StringStruct,
    StringTable,
    VarFileInfo,
    VarStruct,
    VSVersionInfo,
)

with open("VERSION", "r", encoding="utf-8") as _f:
    _version = _f.read().strip()

_version_tuple = tuple(int(part) for part in _version.split(".")) + (0, 0, 0, 0)
_version_tuple = _version_tuple[:4]

_year = "2026"

version_info = VSVersionInfo(
    ffi=FixedFileInfo(
        filevers=_version_tuple,
        prodvers=_version_tuple,
        mask=0x3F,
        flags=0x0,
        OS=0x4,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0),
    ),
    kids=[
        StringFileInfo(
            [
                StringTable(
                    "040904B0",
                    [
                        StringStruct("CompanyName", "Rahul Swargam"),
                        StringStruct("FileDescription", "Image & PDF Toolkit"),
                        StringStruct("FileVersion", _version),
                        StringStruct("InternalName", "ImagePDFToolkit"),
                        StringStruct("LegalCopyright", f"Copyright © {_year} Rahul Swargam"),
                        StringStruct("OriginalFilename", "ImagePDFToolkit.exe"),
                        StringStruct("ProductName", "Image & PDF Toolkit"),
                        StringStruct("ProductVersion", _version),
                    ],
                )
            ]
        ),
        VarFileInfo([VarStruct("Translation", [1033, 1200])]),
    ],
)

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[('assets', 'assets'), ('VERSION', '.')],
    hiddenimports=[],
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
    name='ImagePDFToolkit',
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
    icon=['assets/icons/app.ico'],
    version=version_info,
)
