# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_all

datas = []
binaries = []
hiddenimports = ['pytesseract', 'PIL', 'playwright', 'PyQt5']

# Tesseract dosyalarını ekle
tesseract_path = r'C:\Program Files\Tesseract-OCR'
datas += [(tesseract_path, 'Tesseract-OCR')]

# Playwright browser'ı ekle
browser_path = r'C:\Users\karah\AppData\Local\ms-playwright\chromium-1148\chrome-win'
datas += [(browser_path, 'chrome-win')]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
    a.datas,
    [],
    name='KarahanApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Terminal penceresini kaldırmak için False yaptık
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)