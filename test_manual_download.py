#!/usr/bin/env python3
"""
测试手动下载功能
"""

from chromedriver_updater import ChromeDriverUpdater

def test_manual_download():
    """测试手动下载功能"""
    updater = ChromeDriverUpdater()
    
    # 模拟获取最新版本信息
    system = updater.get_system_info()
    version = "138.0.7204.183"  # 模拟版本号
    
    # 构建下载信息
    download_info = {
        "version": version,
        "system": system,
        "manual_download_url": f"https://storage.googleapis.com/chrome-for-testing-public/{version}/{system}/chromedriver-{system}.zip",
        "manual_instructions": updater.get_manual_download_instructions(system, version)
    }
    
    print("=== 手动下载测试 ===")
    print(f"系统信息: {system}")
    print(f"版本: {version}")
    print(f"下载链接: {download_info['manual_download_url']}")
    print("\n手动下载说明:")
    print(download_info['manual_instructions'])

if __name__ == "__main__":
    test_manual_download() 