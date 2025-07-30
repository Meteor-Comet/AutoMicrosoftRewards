#!/usr/bin/env python3
"""
Microsoft Rewards GUI 简单打包脚本
解决 PyInstaller 启动问题
"""

import os
import sys
import subprocess
import shutil

def main():
    """主函数"""
    print("🚀 Microsoft Rewards GUI 简单打包工具")
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
    
    # 清理构建目录
    if os.path.exists("build"):
        shutil.rmtree("build")
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("__pycache__"):
        shutil.rmtree("__pycache__")
    
    print("🧹 已清理构建目录")
    
    # 最简单的打包命令
    cmd = [
        "pyinstaller",
        "--onedir",  # 使用目录模式，更稳定
        "--windowed",
        "--name=MicrosoftRewards",
        "--add-data=chromedriver.exe;.",
        "--add-data=custom_search_terms.py;.",
        "--add-data=account_manager.py;.",
        "gui_app.py"
    ]
    
    # 移除不存在的文件
    if not os.path.exists("custom_search_terms.py"):
        cmd = [arg for arg in cmd if not arg.startswith("--add-data=custom_search_terms.py")]
    if not os.path.exists("account_manager.py"):
        cmd = [arg for arg in cmd if not arg.startswith("--add-data=account_manager.py")]
    
    try:
        print("🚀 开始打包...")
        print(f"命令: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✅ 打包成功！")
        
        # 复制必要文件
        if os.path.exists("dist/MicrosoftRewards"):
            files_to_copy = ["chromedriver.exe"]
            if os.path.exists("custom_search_terms.py"):
                files_to_copy.append("custom_search_terms.py")
            if os.path.exists("account_manager.py"):
                files_to_copy.append("account_manager.py")
            
            for file_name in files_to_copy:
                if os.path.exists(file_name):
                    shutil.copy(file_name, "dist/MicrosoftRewards/")
                    print(f"✅ 已复制 {file_name} 到 dist/MicrosoftRewards/")
            
            print("\n🎉 打包完成！")
            print("📁 发布文件:")
            print("  - dist/MicrosoftRewards/ (程序目录)")
            print("  - dist/MicrosoftRewards/MicrosoftRewards.exe (主程序)")
            print("  - dist/MicrosoftRewards/chromedriver.exe (浏览器驱动)")
            if os.path.exists("custom_search_terms.py"):
                print("  - dist/MicrosoftRewards/custom_search_terms.py (自定义搜索词)")
            if os.path.exists("account_manager.py"):
                print("  - dist/MicrosoftRewards/account_manager.py (账号管理模块)")
            
            print("\n📝 使用说明:")
            print("1. 将整个 dist/MicrosoftRewards 目录复制到目标机器")
            print("2. 双击 MicrosoftRewards.exe 运行程序")
            print("3. 确保 chromedriver.exe 与 exe 文件在同一目录")
            
        else:
            print("❌ 未找到生成的程序目录")
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失败: {e}")
        print(f"错误输出: {e.stderr}")
        
        print("\n💡 解决方案:")
        print("1. 确保已安装 PyInstaller: pip install pyinstaller")
        print("2. 尝试重新安装: pip uninstall pyinstaller && pip install pyinstaller")
        print("3. 检查 Python 环境是否正常")
        print("4. 尝试在管理员权限下运行")

if __name__ == "__main__":
    main() 