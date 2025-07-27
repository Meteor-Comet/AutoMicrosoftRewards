#!/usr/bin/env python3
"""
Cookies验证工具
用于诊断cookies文件的问题
"""

import json
import os

def validate_cookies(filename='cookies.txt'):
    """验证cookies文件"""
    print("🔍 开始验证cookies文件...")
    print("=" * 50)
    
    if not os.path.exists(filename):
        print(f"❌ Cookies文件 {filename} 不存在！")
        return False
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            cookies_list = json.load(f)
        
        if not cookies_list:
            print("❌ Cookies文件为空！")
            return False
        
        print(f"📂 文件包含 {len(cookies_list)} 个cookies")
        
        # 分析cookies
        valid_cookies = 0
        invalid_cookies = 0
        domains = set()
        
        for i, cookie in enumerate(cookies_list):
            print(f"\n🔍 检查第 {i+1} 个cookie:")
            
            # 检查必要字段
            name = cookie.get('name', '')
            value = cookie.get('value', '')
            domain = cookie.get('domain', '')
            
            print(f"  名称: {name}")
            print(f"  值: {value[:20]}{'...' if len(value) > 20 else ''}")
            print(f"  域名: {domain}")
            
            # 验证必要字段
            if not name or not value:
                print("  ❌ 缺少必要字段 (name 或 value)")
                invalid_cookies += 1
                continue
            
            # 检查域名
            if domain:
                if domain.startswith('.'):
                    print(f"  ⚠️ 域名以.开头: {domain}")
                    print(f"  🔧 修复后域名: {domain[1:]}")
                    domains.add(domain)
                else:
                    domains.add(domain)
            
            # 检查其他字段
            expiry = cookie.get('expiry')
            if expiry:
                print(f"  过期时间: {expiry}")
            
            path = cookie.get('path', '')
            if path:
                print(f"  路径: {path}")
            
            secure = cookie.get('secure', False)
            if secure:
                print("  安全: 是")
            
            http_only = cookie.get('httpOnly', False)
            if http_only:
                print("  HTTP Only: 是")
            
            valid_cookies += 1
            print("  ✅ 有效")
        
        print("\n" + "=" * 50)
        print("📊 验证结果:")
        print(f"✅ 有效cookies: {valid_cookies}")
        print(f"❌ 无效cookies: {invalid_cookies}")
        print(f"🌐 涉及域名: {len(domains)} 个")
        
        if domains:
            print("\n域名列表:")
            for domain in sorted(domains):
                print(f"  - {domain}")
        
        if invalid_cookies == 0:
            print("\n🎉 所有cookies都有效！")
            return True
        else:
            print(f"\n⚠️ 有 {invalid_cookies} 个无效cookies")
            return False
            
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 验证过程出错: {e}")
        return False

def main():
    print("🚀 Cookies验证工具")
    print("=" * 50)
    
    if validate_cookies():
        print("\n💡 建议: cookies文件正常，可以继续使用")
    else:
        print("\n💡 建议: 重新运行 get_cookie.py 获取新的cookies")

if __name__ == "__main__":
    main() 