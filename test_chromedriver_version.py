#!/usr/bin/env python3
"""
测试ChromeDriver版本获取功能
"""

import os
import subprocess
import re
import platform

def test_chromedriver_version():
    """测试ChromeDriver版本获取"""
    chromedriver_path = "chromedriver.exe"
    
    print("=== ChromeDriver版本测试 ===")
    print(f"当前工作目录: {os.getcwd()}")
    print(f"ChromeDriver路径: {chromedriver_path}")
    print(f"文件是否存在: {os.path.exists(chromedriver_path)}")
    
    if not os.path.exists(chromedriver_path):
        print("❌ ChromeDriver文件不存在")
        return
    
    try:
        # 尝试运行ChromeDriver获取版本
        print("\n正在运行ChromeDriver --version...")
        result = subprocess.run([chromedriver_path, "--version"], 
                             capture_output=True, text=True, timeout=10)
        
        print(f"返回码: {result.returncode}")
        print(f"标准输出: {result.stdout}")
        print(f"标准错误: {result.stderr}")
        
        if result.returncode == 0:
            # 尝试多种正则表达式匹配版本
            patterns = [
                r'ChromeDriver (\d+\.\d+\.\d+\.\d+)',
                r'ChromeDriver (\d+\.\d+\.\d+)',
                r'(\d+\.\d+\.\d+\.\d+)',
                r'(\d+\.\d+\.\d+)'
            ]
            
            for pattern in patterns:
                match = re.search(pattern, result.stdout)
                if match:
                    version = match.group(1)
                    print(f"✅ 找到版本: {version} (使用模式: {pattern})")
                    return version
            
            print("❌ 无法从输出中提取版本号")
            print(f"完整输出: {result.stdout}")
        else:
            print("❌ ChromeDriver运行失败")
            
    except subprocess.TimeoutExpired:
        print("❌ ChromeDriver运行超时")
    except Exception as e:
        print(f"❌ 运行ChromeDriver时出错: {e}")

if __name__ == "__main__":
    test_chromedriver_version() 