#!/usr/bin/env python3
"""
Microsoft Rewards GUI 打包脚本
"""

import os
import sys
import subprocess
import shutil

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
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        print("✅ PyInstaller安装成功")
        return True
    except subprocess.CalledProcessError:
        print("❌ PyInstaller安装失败")
        return False

def build_exe():
    """打包exe"""
    print("🔨 开始打包exe...")
    
    # 检查必要文件
    required_files = ["gui_app.py", "chromedriver.exe"]
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ 缺少必要文件: {', '.join(missing_files)}")
        return False
    
    # 构建命令
    cmd = [
        "pyinstaller",
        "--onefile",  # 打包成单个exe文件
        "--windowed",  # 不显示控制台窗口
        "--name=MicrosoftRewards",  # 设置exe名称
        "--icon=icon.ico",  # 图标文件（如果存在）
        "--add-data=chromedriver.exe;.",  # 包含chromedriver
        "--add-data=custom_search_terms.py;.",  # 包含自定义搜索词文件
        "--add-data=account_manager.py;.",  # 包含账号管理模块
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
    
    # 如果图标文件不存在，移除图标参数
    if not os.path.exists("icon.ico"):
        cmd = [arg for arg in cmd if not arg.startswith("--icon")]
    
    # 如果自定义搜索词文件不存在，移除相关参数
    if not os.path.exists("custom_search_terms.py"):
        cmd = [arg for arg in cmd if not arg.startswith("--add-data=custom_search_terms.py")]
    
    try:
        print("🚀 执行打包命令...")
        print(f"命令: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 打包成功！")
        
        # 检查输出文件
        exe_path = "dist/MicrosoftRewards.exe"
        if os.path.exists(exe_path):
            print(f"📁 exe文件位置: {exe_path}")
            
            # 复制必要文件到dist目录
            if os.path.exists("chromedriver.exe"):
                shutil.copy("chromedriver.exe", "dist/")
                print("✅ 已复制chromedriver.exe到dist目录")
            
            if os.path.exists("custom_search_terms.py"):
                shutil.copy("custom_search_terms.py", "dist/")
                print("✅ 已复制custom_search_terms.py到dist目录")
            
            if os.path.exists("account_manager.py"):
                shutil.copy("account_manager.py", "dist/")
                print("✅ 已复制account_manager.py到dist目录")
            
            print("\n🎉 打包完成！")
            print("📁 发布文件:")
            print("  - dist/MicrosoftRewards.exe (主程序)")
            print("  - dist/chromedriver.exe (浏览器驱动)")
            print("  - dist/custom_search_terms.py (可选，自定义搜索词)")
            print("  - dist/account_manager.py (账号管理模块)")
            
            return True
        else:
            print("❌ 未找到生成的exe文件")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失败: {e}")
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

def main():
    """主函数"""
    print("🚀 Microsoft Rewards GUI 打包工具")
    print("=" * 50)
    
    # 检查PyInstaller
    if not check_pyinstaller():
        print("📦 正在安装PyInstaller...")
        if not install_pyinstaller():
            print("❌ 无法安装PyInstaller，请手动安装: pip install pyinstaller")
            return
    
    # 创建图标（可选）
    if not os.path.exists("icon.ico"):
        print("🎨 创建图标文件...")
        create_icon()
    
    # 开始打包
    if build_exe():
        print("\n🎉 打包成功！")
        print("📝 使用说明:")
        print("1. 将dist目录下的所有文件复制到目标机器")
        print("2. 确保chromedriver.exe与exe文件在同一目录")
        print("3. 双击MicrosoftRewards.exe运行程序")
    else:
        print("\n❌ 打包失败，请检查错误信息")

if __name__ == "__main__":
    main() 