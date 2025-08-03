#!/usr/bin/env python3
"""
Microsoft Rewards GUI 稳定打包脚本
解决 PyInstaller 启动问题
"""

import os
import sys
import subprocess
import shutil
import tempfile

def check_pyinstaller():
    """检查是否安装了pyinstaller"""
    try:
        import PyInstaller
        print("✅ PyInstaller已安装")
        return True
    except ImportError:
        print("❌ PyInstaller未安装")
        return False

def install_pyinstaller():
    """安装pyinstaller"""
    print("📦 正在安装PyInstaller...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller>=5.0.0"])
        print("✅ PyInstaller安装成功")
        return True
    except subprocess.CalledProcessError:
        print("❌ PyInstaller安装失败")
        return False

def clean_build_dirs():
    """清理构建目录"""
    dirs_to_clean = ["build", "dist", "__pycache__"]
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🧹 已清理 {dir_name} 目录")

def create_spec_file():
    """创建spec文件"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['gui_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('chromedriver.exe', '.'),
        ('custom_search_terms.py', '.'),
        ('account_manager.py', '.'),
    ],
    hiddenimports=[
        'selenium',
        'selenium.webdriver',
        'selenium.webdriver.chrome.service',
        'selenium.webdriver.common.by',
        'selenium.webdriver.common.keys',
        'selenium.webdriver.support.ui',
        'selenium.webdriver.support',
        'selenium.common.exceptions',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.scrolledtext',
        'json',
        'threading',
        'time',
        'os',
        'random',
        'sys',
        'datetime',
        'webbrowser',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
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
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
'''
    
    with open('MicrosoftRewards.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ 已创建 MicrosoftRewards.spec 文件")

def build_with_spec():
    """使用spec文件构建"""
    print("🔨 使用spec文件构建...")
    
    cmd = ["pyinstaller", "MicrosoftRewards.spec"]
    
    try:
        print("🚀 执行构建命令...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 构建成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 构建失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def build_alternative():
    """备用构建方法"""
    print("🔨 使用备用构建方法...")
    
    cmd = [
        "pyinstaller",
        "--onedir",  # 使用目录模式而不是单文件
        "--windowed",
        "--name=MicrosoftRewards",
        "--icon=icon.ico" if os.path.exists("icon.ico") else None,
        "--add-data=chromedriver.exe;.",
        "--add-data=custom_search_terms.py;.",
        "--add-data=account_manager.py;.",
        "--hidden-import=selenium",
        "--hidden-import=selenium.webdriver",
        "--hidden-import=selenium.webdriver.chrome.service",
        "--hidden-import=selenium.webdriver.common.by",
        "--hidden-import=selenium.webdriver.common.keys",
        "--hidden-import=selenium.webdriver.support.ui",
        "--hidden-import=selenium.webdriver.support",
        "--hidden-import=selenium.common.exceptions",
        "--hidden-import=tkinter",
        "--hidden-import=tkinter.ttk",
        "--hidden-import=tkinter.messagebox",
        "--hidden-import=tkinter.scrolledtext",
        "--hidden-import=json",
        "--hidden-import=threading",
        "--hidden-import=time",
        "--hidden-import=os",
        "--hidden-import=random",
        "--hidden-import=sys",
        "--hidden-import=datetime",
        "--hidden-import=webbrowser",
        "--collect-all=selenium",
        "--collect-all=tkinter",
        "gui_app.py"
    ]
    
    # 移除None值
    cmd = [arg for arg in cmd if arg is not None]
    
    try:
        print("🚀 执行备用构建命令...")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 备用构建成功！")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 备用构建失败: {e}")
        print(f"错误输出: {e.stderr}")
        return False

def create_icon():
    """创建简单的图标文件"""
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # 创建一个简单的图标
        size = (256, 256)
        image = Image.new('RGBA', size, (0, 120, 212, 255))  # Microsoft蓝色
        
        draw = ImageDraw.Draw(image)
        
        # 绘制简单的图标
        draw.ellipse([50, 50, 206, 206], fill=(255, 255, 255, 255))
        draw.text((128, 128), "MR", fill=(0, 120, 212, 255), anchor="mm")
        
        image.save("icon.ico", format='ICO')
        print("✅ 已创建图标文件 icon.ico")
        return True
    except ImportError:
        print("⚠️ 未安装PIL，跳过图标创建")
        return False
    except Exception as e:
        print(f"❌ 创建图标失败: {e}")
        return False

def copy_files_to_dist():
    """复制必要文件到dist目录"""
    files_to_copy = ["chromedriver.exe", "custom_search_terms.py", "account_manager.py"]
    
    for file_name in files_to_copy:
        if os.path.exists(file_name):
            if os.path.exists("dist/MicrosoftRewards"):
                # 目录模式
                shutil.copy(file_name, "dist/MicrosoftRewards/")
                print(f"✅ 已复制 {file_name} 到 dist/MicrosoftRewards/")
            else:
                # 单文件模式
                shutil.copy(file_name, "dist/")
                print(f"✅ 已复制 {file_name} 到 dist/")

def main():
    """主函数"""
    print("🚀 Microsoft Rewards GUI 稳定打包工具")
    print("=" * 50)
    
    # 检查必要文件
    required_files = ["gui_app.py", "chromedriver.exe"]
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺少必要文件: {', '.join(missing_files)}")
        return
    
    # 检查PyInstaller
    if not check_pyinstaller():
        print("📦 正在安装PyInstaller...")
        if not install_pyinstaller():
            print("❌ 无法安装PyInstaller，请手动安装: pip install pyinstaller")
            return
    
    # 清理构建目录
    clean_build_dirs()
    
    # 创建图标（可选）
    if not os.path.exists("icon.ico"):
        print("🎨 创建图标文件...")
        create_icon()
    
    # 方法1: 使用spec文件构建
    print("\n🔧 方法1: 使用spec文件构建")
    create_spec_file()
    if build_with_spec():
        copy_files_to_dist()
        print("\n🎉 打包成功！")
        print("📁 发布文件:")
        if os.path.exists("dist/MicrosoftRewards.exe"):
            print("  - dist/MicrosoftRewards.exe (主程序)")
            print("  - dist/chromedriver.exe (浏览器驱动)")
            print("  - dist/custom_search_terms.py (可选，自定义搜索词)")
            print("  - dist/account_manager.py (账号管理模块)")
        else:
            print("  - dist/MicrosoftRewards/ (程序目录)")
            print("  - dist/MicrosoftRewards/MicrosoftRewards.exe (主程序)")
        return
    
    # 方法2: 备用构建方法
    print("\n🔧 方法2: 使用备用构建方法")
    if build_alternative():
        copy_files_to_dist()
        print("\n🎉 备用打包成功！")
        print("📁 发布文件:")
        if os.path.exists("dist/MicrosoftRewards.exe"):
            print("  - dist/MicrosoftRewards.exe (主程序)")
            print("  - dist/chromedriver.exe (浏览器驱动)")
            print("  - dist/custom_search_terms.py (可选，自定义搜索词)")
            print("  - dist/account_manager.py (账号管理模块)")
        else:
            print("  - dist/MicrosoftRewards/ (程序目录)")
            print("  - dist/MicrosoftRewards/MicrosoftRewards.exe (主程序)")
        return
    
    print("\n❌ 所有打包方法都失败了")
    print("💡 建议:")
    print("1. 确保Python环境干净")
    print("2. 重新安装PyInstaller: pip uninstall pyinstaller && pip install pyinstaller")
    print("3. 检查是否有杀毒软件干扰")
    print("4. 尝试在管理员权限下运行")

if __name__ == "__main__":
    main() 