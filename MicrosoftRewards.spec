# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

datas = [('chromedriver.exe', '.'), ('custom_search_terms.py', '.'), ('account_manager.py', '.'), ('test_rewards.py', '.')]
binaries = []
hiddenimports = ['selenium', 'selenium.webdriver', 'selenium.webdriver.chrome.service', 'selenium.webdriver.common.by', 'selenium.webdriver.common.keys', 'selenium.webdriver.support.ui', 'selenium.webdriver.support', 'selenium.common.exceptions', 'tkinter', 'tkinter.ttk', 'tkinter.messagebox', 'tkinter.scrolledtext', 'json', 'threading', 'time', 'os', 'random', 'sys', 'datetime', 'webbrowser']
tmp_ret = collect_all('selenium')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('tkinter')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['gui_app.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
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
