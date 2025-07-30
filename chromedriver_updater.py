# #!/usr/bin/env python3
# """
# ChromeDriver 自动更新模块
# """

import requests
import os
import zipfile
import shutil
import platform
import subprocess
import re
from urllib.parse import urlparse
import threading
import time

class ChromeDriverUpdater:
    def __init__(self):
        # 指定网页 URL（根据实际页面结构调整）
        self.page_url = "https://googlechromelabs.github.io/chrome-for-testing/#stable"
        self.download_base_url = "https://storage.googleapis.com/chrome-for-testing-public"
        self.current_driver_path = "chromedriver.exe"  # 可根据平台修改为 chromedriver 或 chromedriver-linux 等

    def get_system_info(self):
        """获取系统信息"""
        system = platform.system().lower()
        machine = platform.machine().lower()
        print(f"检测到的系统类型: {system}")
        print(f"检测到的机器架构: {machine}")
        
        if system == "windows":
            if "64" in machine or "x86_64" in machine:
                result = "win64"
            else:
                result = "win32"
        elif system == "linux":
            result = "linux64"
        elif system == "darwin":  # macOS
            if "arm" in machine:
                result = "mac-arm64"
            else:
                result = "mac-x64"
        else:
            result = "win64"  # 默认返回Windows 64位
            
        print(f"选择的平台标识: {result}")
        return result

    def get_current_chromedriver_version(self):
        """从当前目录获取 chromedriver 版本"""
        try:
            if not os.path.exists(self.current_driver_path):
                return None

            # 使用完整路径来确保使用当前目录的chromedriver
            driver_path = os.path.abspath(self.current_driver_path)
            result = subprocess.run([driver_path, "--version"],
                                    capture_output=True, text=True)
            version_match = re.search(r'ChromeDriver (\d+\.\d+\.\d+\.\d+)', result.stdout)
            if version_match:
                return version_match.group(1)
        except Exception as e:
            print(f"获取当前ChromeDriver版本时出错: {e}")
        return None

    def get_latest_chromedriver_info(self):
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.7204.183 Safari/537.36"
            }
            response = requests.get(self.page_url, headers=headers, timeout=10)
            response.raise_for_status()
            html = response.text
            # print("网页内容:", html)  # 调试用

            version_match = re.search(r'<h2>Stable</h2>.*?<code>(\d+\.\d+\.\d+\.\d+)</code>', html, re.DOTALL)
            if not version_match:
                raise Exception("未找到版本信息")

            latest_version = version_match.group(1)
            system = self.get_system_info()
            download_url = f"{self.download_base_url}/{latest_version}/{system}/chromedriver-{system}.zip"
            
            print(f"构建的下载URL: {download_url}")
            
            return {
                "version": latest_version,
                "download_url": download_url,
                "system": system,
                "manual_download_url": download_url,
                "manual_instructions": self.get_manual_download_instructions(system, latest_version)
            }
        except Exception as e:
            print(f"获取最新ChromeDriver信息时出错: {e}")
            return None

    def get_manual_download_instructions(self, system, version):
        """获取手动下载说明"""
        instructions = f"""
手动下载ChromeDriver {version} 说明：

1. 访问官方下载页面：https://googlechromelabs.github.io/chrome-for-testing/#stable

2. 找到 "chromedriver" 部分，下载对应平台的版本：
   - 当前检测到的平台：{system}
   - 直接下载链接：https://storage.googleapis.com/chrome-for-testing-public/{version}/{system}/chromedriver-{system}.zip

3. 下载完成后：
   - 解压zip文件
   - 将解压出的 chromedriver.exe 文件复制到当前程序目录
   - 替换现有的 chromedriver.exe 文件

4. 验证安装：
   - 运行 .\\chromedriver.exe --version 检查版本
   - 应该显示：ChromeDriver {version}

注意：确保下载的是 {system} 版本，否则可能无法正常运行。
"""
        return instructions


    def download_chromedriver(self, download_url, callback=None):
        """下载并解压到当前目录"""
        try:
            temp_dir = "temp_chromedriver"
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)

            if callback:
                callback("正在下载ChromeDriver...")

            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()

            zip_path = os.path.join(temp_dir, "chromedriver.zip")
            with open(zip_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # 检查下载的zip文件大小
            zip_size = os.path.getsize(zip_path)
            print(f"下载的zip文件大小: {zip_size:,} 字节")
            
            if callback:
                callback("正在解压文件...")

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                # 列出zip文件中的所有内容
                print("ZIP文件内容:")
                for info in zip_ref.infolist():
                    print(f"  - {info.filename} ({info.file_size:,} 字节)")
                
                zip_ref.extractall(temp_dir)

            chromedriver_file = None
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.startswith("chromedriver") and file.endswith(".exe"):
                        chromedriver_file = os.path.join(root, file)
                        file_size = os.path.getsize(chromedriver_file)
                        print(f"找到chromedriver文件: {chromedriver_file} ({file_size:,} 字节)")
                        break
                if chromedriver_file:
                    break

            if not chromedriver_file:
                # 如果没找到，列出temp_dir中的所有文件进行调试
                print("未找到chromedriver.exe，temp_dir中的文件:")
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_size = os.path.getsize(file_path)
                        print(f"  - {file_path} ({file_size:,} 字节)")
                raise Exception("解压后未找到chromedriver.exe文件")

            if callback:
                callback("正在替换旧版本...")

            backup_path = f"{self.current_driver_path}.backup"
            if os.path.exists(self.current_driver_path):
                shutil.move(self.current_driver_path, backup_path)

            shutil.copy2(chromedriver_file, self.current_driver_path)
            
            # 检查最终文件大小
            final_size = os.path.getsize(self.current_driver_path)
            print(f"最终chromedriver.exe大小: {final_size:,} 字节")

            if platform.system().lower() != "windows":
                os.chmod(self.current_driver_path, 0o755)

            shutil.rmtree(temp_dir)

            if callback:
                callback("ChromeDriver更新完成！")

            return True

        except Exception as e:
            if callback:
                callback(f"更新失败: {str(e)}")
            if 'backup_path' in locals() and os.path.exists(backup_path) and os.path.exists(self.current_driver_path):
                shutil.move(backup_path, self.current_driver_path)
            return False

    def check_for_updates(self, callback=None):
        try:
            if callback:
                callback("正在检查ChromeDriver版本...")

            current_driver_version = self.get_current_chromedriver_version()
            if callback:
                if current_driver_version:
                    callback(f"当前ChromeDriver版本: {current_driver_version}")
                else:
                    callback("未找到ChromeDriver，需要下载")

            latest_info = self.get_latest_chromedriver_info()
            if not latest_info:
                if callback:
                    callback("无法获取最新版本信息")
                return None

            if callback:
                callback(f"最新ChromeDriver版本: {latest_info['version']}")

            if current_driver_version:
                current_major = current_driver_version.split('.')[0]
                latest_major = latest_info['version'].split('.')[0]

                if current_major == latest_major:
                    if callback:
                        callback("ChromeDriver已是最新版本")
                    return None
                else:
                    if callback:
                        callback("发现新版本，建议更新")
                    return latest_info
            else:
                if callback:
                    callback("需要下载ChromeDriver")
                return latest_info

        except Exception as e:
            if callback:
                callback(f"检查更新时出错: {str(e)}")
            return None

    def update_chromedriver(self, callback=None):
        latest_info = self.check_for_updates(callback)
        if not latest_info:
            return False
        return self.download_chromedriver(latest_info['download_url'], callback)

    def force_update_chromedriver(self, callback=None):
        try:
            if callback:
                callback("正在获取最新ChromeDriver信息...")
            latest_info = self.get_latest_chromedriver_info()
            if not latest_info:
                if callback:
                    callback("无法获取最新版本信息")
                return False
            if callback:
                callback(f"正在下载最新版本: {latest_info['version']}")
            return self.download_chromedriver(latest_info['download_url'], callback)
        except Exception as e:
            if callback:
                callback(f"强制更新时出错: {str(e)}")
            return False

def test_chromedriver_updater():
    """测试ChromeDriver更新器"""
    updater = ChromeDriverUpdater()

    def callback(message):
        print(message)

    print("=== ChromeDriver 更新测试 ===")
    print(f"系统信息: {updater.get_system_info()}")

    current_driver_version = updater.get_current_chromedriver_version()
    print(f"当前ChromeDriver版本: {current_driver_version}")

    latest_info = updater.get_latest_chromedriver_info()
    if latest_info:
        print(f"最新版本信息: {latest_info['version']}")
        print(f"下载链接: {latest_info['manual_download_url']}")

    print("\n选择操作:")
    print("1. 检查更新（比较版本）")
    print("2. 强制更新（下载最新版本）")
    print("3. 显示手动下载说明")
    print("4. 退出")

    choice = input("请选择 (1/2/3/4): ").strip()

    if choice == "1":
        update_info = updater.check_for_updates(callback)
        if update_info:
            print("发现更新")
            print(f"最新版本: {update_info['version']}")
            print(f"下载链接: {update_info['manual_download_url']}")
            response = input("是否要自动更新ChromeDriver? (y/n): ")
            if response.lower() == 'y':
                success = updater.update_chromedriver(callback)
                if success:
                    print("更新成功！")
                else:
                    print("自动更新失败！")
                    print("请尝试手动下载：")
                    print(update_info['manual_instructions'])
            else:
                print("手动下载说明：")
                print(update_info['manual_instructions'])
        else:
            print("无需更新")

    elif choice == "2":
        print("开始强制更新...")
        success = updater.force_update_chromedriver(callback)
        if success:
            print("强制更新成功！")
        else:
            print("强制更新失败！")
            if latest_info:
                print("请尝试手动下载：")
                print(latest_info['manual_instructions'])

    elif choice == "3":
        if latest_info:
            print("手动下载说明：")
            print(latest_info['manual_instructions'])
        else:
            print("无法获取最新版本信息，请检查网络连接")

    elif choice == "4":
        print("退出")

    else:
        print("无效选择")

if __name__ == "__main__":
    test_chromedriver_updater()
