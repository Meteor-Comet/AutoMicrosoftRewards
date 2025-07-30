#!/usr/bin/env python3
"""
智能登录检测脚本
能够处理登录页面跳转的情况
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
import time
import json

def check_login_status_smart(driver):
    """智能检查登录状态"""
    try:
        current_url = driver.current_url
        print(f"当前页面URL: {current_url}")
        
        # 检查是否在登录页面
        if "login" in current_url.lower() or "account" in current_url.lower():
            print("⚠️ 当前在登录页面，等待登录完成...")
            return False
        
        # 检查是否在必应首页
        if "bing.com" in current_url and "login" not in current_url.lower():
            print("✅ 当前在必应首页")
            
            # 检查用户头像/用户名
            try:
                user_elements = driver.find_elements(By.CSS_SELECTOR, 
                    "[data-testid='user-avatar'], .user-avatar, .user-name, [aria-label*='用户'], [aria-label*='User'], .user-info")
                if user_elements:
                    print("✅ 检测到用户头像/用户名元素，登录成功！")
                    return True
            except:
                pass
            
            # 检查登录按钮状态
            try:
                login_element = driver.find_element(By.ID, "id_s")
                login_text = login_element.text.strip()
                print(f"登录按钮文本: '{login_text}'")
                
                if login_text != "登录":
                    print("✅ 登录按钮文本已变化，登录成功！")
                    return True
                else:
                    print("⏳ 登录按钮仍显示'登录'，等待登录...")
                    return False
            except NoSuchElementException:
                print("未找到登录按钮，检查其他登录标志...")
                
                # 检查搜索框
                try:
                    search_box = driver.find_element(By.ID, "sb_form_q")
                    print("✅ 检测到搜索框，可能已登录")
                    return True
                except:
                    pass
                
                # 检查是否有其他登录成功的标志
                try:
                    # 检查是否有个人设置或账户相关元素
                    account_elements = driver.find_elements(By.CSS_SELECTOR, 
                        "[aria-label*='账户'], [aria-label*='Account'], .account-menu, .user-menu")
                    if account_elements:
                        print("✅ 检测到账户相关元素，登录成功！")
                        return True
                except:
                    pass
                
                return False
        else:
            print(f"⚠️ 当前不在必应首页: {current_url}")
            return False
            
    except Exception as e:
        print(f"检查登录状态时出错: {e}")
        return False

def wait_for_login_smart(driver, timeout=300):
    """智能等待用户登录"""
    print("=" * 50)
    print("请在浏览器中手动登录账户...")
    print("程序将智能检测登录状态...")
    print("=" * 50)
    
    start_time = time.time()
    check_count = 0
    
    while time.time() - start_time < timeout:
        check_count += 1
        remaining_time = int(timeout - (time.time() - start_time))
        
        print(f"\n第{check_count}次检查登录状态... (剩余时间: {remaining_time}秒)")
        
        if check_login_status_smart(driver):
            print("🎉 检测到登录成功！")
            return True
        
        # 每5秒检查一次
        time.sleep(5)
    
    print("❌ 等待登录超时！")
    return False

def save_cookies(driver, filename='cookies.txt'):
    """保存cookies到文件"""
    try:
        cookies = driver.get_cookies()
        
        if not cookies:
            print("⚠️ 警告: 没有获取到任何cookies")
            return False
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Cookies已保存到 {filename}")
        print(f"📊 共保存了 {len(cookies)} 个cookies")
        return True
    except Exception as e:
        print(f"❌ 保存cookies时出错: {e}")
        return False

def setup_driver():
    """设置Chrome驱动"""
    try:
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # 指定当前目录下的chromedriver.exe
        chromedriver_path = "./chromedriver.exe"
        service = Service(executable_path=chromedriver_path)
        
        driver = webdriver.Chrome(service=service, options=options)
        
        # 执行脚本来隐藏webdriver特征
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
    except Exception as e:
        print(f"❌ 初始化Chrome驱动失败: {e}")
        return None

def main():
    print("🚀 启动智能Microsoft Rewards Cookie获取工具")
    print("=" * 50)
    
    # 初始化Chrome驱动
    driver = setup_driver()
    if not driver:
        return
    
    try:
        # 访问必应首页
        print("🌐 正在访问必应首页...")
        driver.get('https://cn.bing.com/?mkt=zh-CN')
        
        # 等待页面加载
        print("⏳ 等待页面加载...")
        time.sleep(3)
        
        # 智能等待用户登录
        if wait_for_login_smart(driver):
            # 登录成功后保存cookies
            if save_cookies(driver):
                print("🎉 程序执行完成！")
                print("💡 提示: 现在可以使用search.py进行自动搜索了")
            else:
                print("❌ 保存cookies失败！")
        else:
            print("❌ 登录超时，程序退出！")
            
    except KeyboardInterrupt:
        print("\n⚠️ 用户中断程序")
    except Exception as e:
        print(f"❌ 程序执行出错: {e}")
    finally:
        # 关闭浏览器
        print("🔒 正在关闭浏览器...")
        driver.quit()
        print("✅ 程序已退出")

if __name__ == "__main__":
    main() 