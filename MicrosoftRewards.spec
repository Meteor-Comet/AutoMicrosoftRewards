# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['gui_app.py'],
    pathex=[],
    binaries=[],
    datas=[('chromedriver.exe', '.'), ('custom_search_terms.py', '.')],
    hiddenimports=['selenium', 'selenium.webdriver', 'selenium.webdriver.chrome.service', 'selenium.webdriver.common.by', 'selenium.webdriver.common.keys', 'selenium.webdriver.support.ui', 'selenium.webdriver.support', 'selenium.common.exceptions'],
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
    name='MicrosoftRewards',
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
    icon=['icon.ico'],
)
