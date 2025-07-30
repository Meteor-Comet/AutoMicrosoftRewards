# #!/usr/bin/env python3
# """
# ChromeDriver 自动更新模块
# """

# import requests
# import json
# import os
# import zipfile
# import shutil
# import platform
# import subprocess
# import re
# from urllib.parse import urlparse
# import threading
# import time

# class ChromeDriverUpdater:
#     def __init__(self):
#         self.api_url = "https://googlechromelabs.github.io/chrome-for-testing/latest-versions-per-milestone.json"
#         self.download_base_url = "https://storage.googleapis.com/chrome-for-testing-public"
#         self.current_driver_path = "chromedriver.exe"
        
#     def get_system_info(self):
#         """获取系统信息"""
#         system = platform.system().lower()
#         machine = platform.machine().lower()
        
#         if system == "windows":
#             if "64" in machine or "x86_64" in machine:
#                 return "win64"
#             else:
#                 return "win32"
#         elif system == "linux":
#             return "linux64"
#         elif system == "darwin":  # macOS
#             if "arm" in machine:
#                 return "mac-arm64"
#             else:
#                 return "mac-x64"
#         else:
#             return "win64"  # 默认返回Windows 64位
    
#     def get_chrome_version(self):
#         """获取本地Chrome浏览器版本"""
#         try:
#             system = platform.system().lower()
#             if system == "windows":
#                 # Windows下检查Chrome版本
#                 import winreg
#                 try:
#                     key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
#                                         r"Software\Google\Chrome\BLBeacon")
#                     version, _ = winreg.QueryValueEx(key, "version")
#                     return version
#                 except:
#                     # 尝试从Program Files获取
#                     chrome_paths = [
#                         r"C:\Program Files\Google\Chrome\Application\chrome.exe",
#                         r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
#                     ]
#                     for path in chrome_paths:
#                         if os.path.exists(path):
#                             try:
#                                 result = subprocess.run([path, "--version"], 
#                                                      capture_output=True, text=True)
#                                 version_match = re.search(r'Chrome/(\d+\.\d+\.\d+\.\d+)', 
#                                                         result.stdout)
#                                 if version_match:
#                                     return version_match.group(1)
#                             except:
#                                 continue
#             elif system == "linux":
#                 # Linux下检查Chrome版本
#                 try:
#                     result = subprocess.run(["google-chrome", "--version"], 
#                                          capture_output=True, text=True)
#                     version_match = re.search(r'Google Chrome (\d+\.\d+\.\d+\.\d+)', 
#                                             result.stdout)
#                     if version_match:
#                         return version_match.group(1)
#                 except:
#                     pass
#             elif system == "darwin":  # macOS
#                 try:
#                     result = subprocess.run(["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", 
#                                           "--version"], capture_output=True, text=True)
#                     version_match = re.search(r'Google Chrome (\d+\.\d+\.\d+\.\d+)', 
#                                             result.stdout)
#                     if version_match:
#                         return version_match.group(1)
#                 except:
#                     pass
#         except Exception as e:
#             print(f"获取Chrome版本时出错: {e}")
        
#         return None
    
#     def get_latest_chromedriver_info(self):
#         """获取最新的ChromeDriver信息"""
#         try:
#             response = requests.get(self.api_url, timeout=10)
#             response.raise_for_status()
#             data = response.json()
            
#             # 获取最新稳定版本
#             latest_version = None
#             if isinstance(data, dict):
#                 for milestone in data:
#                     if isinstance(data[milestone], dict) and data[milestone].get("version"):
#                         latest_version = data[milestone]["version"]
#                         break
            
#             if not latest_version:
#                 return None
            
#             # 构建下载URL
#             system = self.get_system_info()
#             download_url = f"{self.download_base_url}/{latest_version}/{system}/chromedriver-{system}.zip"
            
#             return {
#                 "version": latest_version,
#                 "download_url": download_url,
#                 "system": system
#             }
#         except Exception as e:
#             print(f"获取最新ChromeDriver信息时出错: {e}")
#             return None
    
#     def get_current_chromedriver_version(self):
#         """获取当前ChromeDriver版本"""
#         try:
#             if not os.path.exists(self.current_driver_path):
#                 return None
            
#             result = subprocess.run([self.current_driver_path, "--version"], 
#                                  capture_output=True, text=True)
#             version_match = re.search(r'ChromeDriver (\d+\.\d+\.\d+\.\d+)', 
#                                     result.stdout)
#             if version_match:
#                 return version_match.group(1)
#         except Exception as e:
#             print(f"获取当前ChromeDriver版本时出错: {e}")
        
#         return None
    
#     def download_chromedriver(self, download_url, callback=None):
#         """下载ChromeDriver"""
#         try:
#             # 创建临时目录
#             temp_dir = "temp_chromedriver"
#             if os.path.exists(temp_dir):
#                 shutil.rmtree(temp_dir)
#             os.makedirs(temp_dir)
            
#             # 下载文件
#             if callback:
#                 callback("正在下载ChromeDriver...")
            
#             response = requests.get(download_url, stream=True, timeout=30)
#             response.raise_for_status()
            
#             zip_path = os.path.join(temp_dir, "chromedriver.zip")
#             with open(zip_path, 'wb') as f:
#                 for chunk in response.iter_content(chunk_size=8192):
#                     f.write(chunk)
            
#             if callback:
#                 callback("正在解压文件...")
            
#             # 解压文件
#             with zipfile.ZipFile(zip_path, 'r') as zip_ref:
#                 zip_ref.extractall(temp_dir)
            
#             # 查找chromedriver文件
#             chromedriver_file = None
#             for root, dirs, files in os.walk(temp_dir):
#                 for file in files:
#                     if file.startswith("chromedriver"):
#                         chromedriver_file = os.path.join(root, file)
#                         break
#                 if chromedriver_file:
#                     break
            
#             if not chromedriver_file:
#                 raise Exception("解压后未找到chromedriver文件")
            
#             if callback:
#                 callback("正在替换旧版本...")
            
#             # 备份旧版本
#             backup_path = None
#             if os.path.exists(self.current_driver_path):
#                 backup_path = f"{self.current_driver_path}.backup"
#                 shutil.move(self.current_driver_path, backup_path)
            
#             # 复制新版本
#             shutil.copy2(chromedriver_file, self.current_driver_path)
            
#             # 设置执行权限（Linux/macOS）
#             if platform.system().lower() != "windows":
#                 os.chmod(self.current_driver_path, 0o755)
            
#             # 清理临时文件
#             shutil.rmtree(temp_dir)
            
#             if callback:
#                 callback("ChromeDriver更新完成！")
            
#             return True
            
#         except Exception as e:
#             # 恢复备份
#             if backup_path and os.path.exists(backup_path):
#                 shutil.move(backup_path, self.current_driver_path)
            
#             if callback:
#                 callback(f"更新失败: {str(e)}")
            
#             return False
    
#     def check_for_updates(self, callback=None):
#         """检查更新"""
#         try:
#             if callback:
#                 callback("正在检查ChromeDriver版本...")
            
#             current_driver_version = self.get_current_chromedriver_version()
#             if callback:
#                 if current_driver_version:
#                     callback(f"当前ChromeDriver版本: {current_driver_version}")
#                 else:
#                     callback("未找到ChromeDriver，需要下载")
            
#             latest_info = self.get_latest_chromedriver_info()
#             if not latest_info:
#                 if callback:
#                     callback("无法获取最新版本信息")
#                 return None
            
#             if callback:
#                 callback(f"最新ChromeDriver版本: {latest_info['version']}")
            
#             # 比较版本
#             if current_driver_version:
#                 current_major = current_driver_version.split('.')[0]
#                 latest_major = latest_info['version'].split('.')[0]
                
#                 if current_major == latest_major:
#                     if callback:
#                         callback("ChromeDriver已是最新版本")
#                     return None
#                 else:
#                     if callback:
#                         callback("发现新版本，建议更新")
#                     return latest_info
#             else:
#                 if callback:
#                     callback("需要下载ChromeDriver")
#                 return latest_info
                
#         except Exception as e:
#             if callback:
#                 callback(f"检查更新时出错: {str(e)}")
#             return None
    
#     def update_chromedriver(self, callback=None):
#         """更新ChromeDriver"""
#         latest_info = self.check_for_updates(callback)
#         if not latest_info:
#             return False
        
#         return self.download_chromedriver(latest_info['download_url'], callback)
    
#     def force_update_chromedriver(self, callback=None):
#         """强制更新ChromeDriver（不管当前版本）"""
#         try:
#             if callback:
#                 callback("正在获取最新ChromeDriver信息...")
            
#             latest_info = self.get_latest_chromedriver_info()
#             if not latest_info:
#                 if callback:
#                     callback("无法获取最新版本信息")
#                 return False
            
#             if callback:
#                 callback(f"正在下载最新版本: {latest_info['version']}")
            
#             return self.download_chromedriver(latest_info['download_url'], callback)
            
#         except Exception as e:
#             if callback:
#                 callback(f"强制更新时出错: {str(e)}")
#             return False

# def test_chromedriver_updater():
#     """测试ChromeDriver更新器"""
#     updater = ChromeDriverUpdater()
    
#     def callback(message):
#         print(message)
    
#     print("=== ChromeDriver 更新测试 ===")
#     print(f"系统信息: {updater.get_system_info()}")
    
#     current_driver_version = updater.get_current_chromedriver_version()
#     print(f"当前ChromeDriver版本: {current_driver_version}")
    
#     latest_info = updater.get_latest_chromedriver_info()
#     if latest_info:
#         print(f"最新版本信息: {latest_info}")
    
#     print("\n选择操作:")
#     print("1. 检查更新（比较版本）")
#     print("2. 强制更新（下载最新版本）")
#     print("3. 退出")
    
#     choice = input("请选择 (1/2/3): ").strip()
    
#     if choice == "1":
#         # 检查更新
#         update_info = updater.check_for_updates(callback)
#         if update_info:
#             print("发现更新")
#             # 询问是否更新
#             response = input("是否要更新ChromeDriver? (y/n): ")
#             if response.lower() == 'y':
#                 success = updater.update_chromedriver(callback)
#                 if success:
#                     print("更新成功！")
#                 else:
#                     print("更新失败！")
#         else:
#             print("无需更新")
    
#     elif choice == "2":
#         # 强制更新
#         print("开始强制更新...")
#         success = updater.force_update_chromedriver(callback)
#         if success:
#             print("强制更新成功！")
#         else:
#             print("强制更新失败！")
    
#     elif choice == "3":
#         print("退出")
    
#     else:
#         print("无效选择")

# if __name__ == "__main__":
#     test_chromedriver_updater() 
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

        if system == "windows":
            if "64" in machine or "x86_64" in machine:
                return "win64"
            else:
                return "win32"
        elif system == "linux":
            return "linux64"
        elif system == "darwin":  # macOS
            if "arm" in machine:
                return "mac-arm64"
            else:
                return "mac-x64"
        else:
            return "win64"  # 默认返回Windows 64位

    def get_current_chromedriver_version(self):
        """从当前目录获取 chromedriver 版本"""
        try:
            if not os.path.exists(self.current_driver_path):
                return None

            result = subprocess.run([self.current_driver_path, "--version"],
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
            return {
                "version": latest_version,
                "download_url": download_url,
                "system": system
            }
        except Exception as e:
            print(f"获取最新ChromeDriver信息时出错: {e}")
            return None


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

            if callback:
                callback("正在解压文件...")

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            chromedriver_file = None
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.startswith("chromedriver"):
                        chromedriver_file = os.path.join(root, file)
                        break
                if chromedriver_file:
                    break

            if not chromedriver_file:
                raise Exception("解压后未找到chromedriver文件")

            if callback:
                callback("正在替换旧版本...")

            backup_path = f"{self.current_driver_path}.backup"
            if os.path.exists(self.current_driver_path):
                shutil.move(self.current_driver_path, backup_path)

            shutil.copy2(chromedriver_file, self.current_driver_path)

            if platform.system().lower() != "windows":
                os.chmod(self.current_driver_path, 0o755)

            shutil.rmtree(temp_dir)

            if callback:
                callback("ChromeDriver更新完成！")

            return True

        except Exception as e:
            if callback:
                callback(f"更新失败: {str(e)}")
            if os.path.exists(backup_path) and os.path.exists(self.current_driver_path):
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
        print(f"最新版本信息: {latest_info}")

    print("\n选择操作:")
    print("1. 检查更新（比较版本）")
    print("2. 强制更新（下载最新版本）")
    print("3. 退出")

    choice = input("请选择 (1/2/3): ").strip()

    if choice == "1":
        update_info = updater.check_for_updates(callback)
        if update_info:
            print("发现更新")
            response = input("是否要更新ChromeDriver? (y/n): ")
            if response.lower() == 'y':
                success = updater.update_chromedriver(callback)
                if success:
                    print("更新成功！")
                else:
                    print("更新失败！")
        else:
            print("无需更新")

    elif choice == "2":
        print("开始强制更新...")
        success = updater.force_update_chromedriver(callback)
        if success:
            print("强制更新成功！")
        else:
            print("强制更新失败！")

    elif choice == "3":
        print("退出")

    else:
        print("无效选择")

if __name__ == "__main__":
    test_chromedriver_updater()
