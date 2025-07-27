#!/usr/bin/env python3
"""
Microsoft Rewards 桌面端自动搜索工具
"""

import json
import time
import os
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys

# 尝试导入自定义搜索词，如果没有则使用默认列表
try:
    from custom_search_terms import CUSTOM_SEARCH_TERMS
    RANDOM_SEARCH_TERMS = CUSTOM_SEARCH_TERMS
    print("✅ 使用自定义搜索词列表")
except ImportError:
    # 默认随机搜索词列表
    RANDOM_SEARCH_TERMS = [
        "天气", "新闻", "美食", "旅游", "电影", "音乐", "游戏", "科技", "健康", "教育",
        "购物", "汽车", "房产", "股票", "基金", "理财", "保险", "银行", "信用卡", "贷款",
        "手机", "电脑", "相机", "耳机", "手表", "包包", "鞋子", "衣服", "化妆品", "香水",
        "咖啡", "茶", "酒", "饮料", "零食", "水果", "蔬菜", "肉类", "海鲜", "甜点",
        "运动", "健身", "瑜伽", "跑步", "游泳", "篮球", "足球", "网球", "高尔夫", "滑雪",
        "读书", "写作", "绘画", "摄影", "园艺", "烹饪", "手工", "收藏", "宠物", "植物",
        "历史", "地理", "文化", "艺术", "科学", "数学", "物理", "化学", "生物", "医学",
        "经济", "政治", "社会", "环境", "能源", "交通", "通信", "互联网", "人工智能", "大数据",
        "云计算", "区块链", "物联网", "5G", "虚拟现实", "增强现实", "机器人", "无人机", "自动驾驶", "新能源",
        "环保", "可持续发展", "绿色能源", "循环经济", "碳中和", "气候变化", "生物多样性", "海洋保护", "森林保护", "野生动物"
    ]
    print("✅ 使用默认搜索词列表")

def get_random_search_term():
    """获取随机搜索词"""
    return random.choice(RANDOM_SEARCH_TERMS)

def setup_driver(options=None):
    """设置Chrome驱动"""
    try:
        if options is None:
            options = webdriver.ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("--mute-audio")

        chromedriver_path = "./chromedriver.exe"
        service = Service(executable_path=chromedriver_path)
        
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.maximize_window()
        return driver
    except Exception as e:
        print(f"❌ 初始化Chrome驱动失败: {e}")
        return None

def load_cookies(driver, filename='cookies.txt'):
    """加载cookies"""
    try:
        if not os.path.exists(filename):
            print(f"❌ Cookies文件不存在: {filename}")
            return False
        
        with open(filename, 'r', encoding='utf-8') as f:
            cookies_list = json.load(f)
        
        print(f"📂 加载了 {len(cookies_list)} 个cookies")
        
        # 先访问必应网站
        print("🌐 先访问必应网站...")
        driver.get('https://cn.bing.com')
        time.sleep(2)
        driver.delete_all_cookies()
        
        valid_cookies = 0
        invalid_cookies = 0
        
        for cookie in cookies_list:
            try:
                if not cookie.get('name') or not cookie.get('value'):
                    invalid_cookies += 1
                    continue
                
                if isinstance(cookie.get('expiry'), float):
                    cookie['expiry'] = int(cookie['expiry'])
                
                if 'domain' in cookie:
                    domain = cookie['domain']
                    if domain.startswith('.'):
                        cookie['domain'] = domain[1:]
                
                driver.add_cookie(cookie)
                valid_cookies += 1
            except Exception as e:
                print(f"⚠️ 跳过无效cookie: {cookie.get('name', 'unknown')} - {str(e)}")
                invalid_cookies += 1
                continue
        
        print(f"✅ 成功加载 {valid_cookies} 个cookies")
        if invalid_cookies > 0:
            print(f"⚠️ 跳过了 {invalid_cookies} 个无效cookies")
        
        return valid_cookies > 0
    except Exception as e:
        print(f"❌ 加载cookies时出错: {e}")
        return False

def desktop_search(driver):
    """桌面端搜索"""
    print("🖥️ 开始桌面端搜索...")
    try:
        driver.get('https://cn.bing.com')
        time.sleep(3)
        
        for i in range(30):
            try:
                search_box = driver.find_element(By.ID, "sb_form_q")
                search_box.clear()
                search_term = get_random_search_term()
                search_box.send_keys(search_term)
                time.sleep(1)
                search_box.send_keys(Keys.RETURN)
                print(f"🖥️ 桌面搜索 {i+1}/30: '{search_term}'")
                time.sleep(8)
            except Exception as e:
                print(f"⚠️ 第{i+1}次搜索出错: {e}")
                driver.get('https://cn.bing.com')
                time.sleep(3)
                continue
        
        print("✅ 桌面端搜索完成")
        return True
    except Exception as e:
        print(f"❌ 桌面端搜索出错: {e}")
        return False

def main():
    """主函数"""
    print("🚀 启动Microsoft Rewards桌面端自动搜索工具")
    print("=" * 50)
    
    driver = setup_driver()
    if not driver:
        print("❌ 无法初始化浏览器驱动")
        return
    
    try:
        # 加载cookies
        if not load_cookies(driver):
            print("⚠️ Cookies加载失败，但继续尝试搜索...")
        
        driver.refresh()
        time.sleep(3)
        
        # 执行桌面端搜索
        if desktop_search(driver):
            print("🎉 桌面端搜索任务完成！")
        else:
            print("❌ 桌面端搜索任务失败")
    
    except Exception as e:
        print(f"❌ 程序执行出错: {e}")
    
    finally:
        print("🔒 正在关闭浏览器...")
        driver.quit()
        print("✅ 程序已退出")

if __name__ == "__main__":
    main() 