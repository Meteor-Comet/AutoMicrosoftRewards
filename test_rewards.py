#!/usr/bin/env python3
"""
积分任务测试脚本
用于调试积分任务功能
"""

import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

def test_rewards_task():
    """测试积分任务功能"""
    print("🎯 开始测试积分任务功能...")
    
    try:
        # 设置Chrome选项
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--mute-audio")
        # 禁用日志输出
        options.add_argument("--log-level=3")
        options.add_argument("--silent")
        
        # 初始化驱动
        chromedriver_path = "./chromedriver.exe"
        service = Service(executable_path=chromedriver_path)
        
        driver = webdriver.Chrome(service=service, options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.maximize_window()
        
        # 加载cookies
        try:
            with open('cookies.txt', 'r', encoding='utf-8') as f:
                cookies_list = json.load(f)
            
            print(f"📂 加载了 {len(cookies_list)} 个cookies")
            
            # 先访问必应网站
            driver.get('https://cn.bing.com')
            time.sleep(2)
            driver.delete_all_cookies()
            
            valid_cookies = 0
            for cookie in cookies_list:
                try:
                    if not cookie.get('name') or not cookie.get('value'):
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
                    continue
            
            print(f"✅ 成功加载 {valid_cookies} 个cookies")
            
        except Exception as e:
            print(f"⚠️ Cookies加载失败: {e}")
        
        # 访问必应首页
        driver.get('https://cn.bing.com')
        time.sleep(5)
        
        print("🔍 开始查找积分侧栏...")
        
        # 方法1: 尝试直接访问rewards页面
        try:
            print("🔄 尝试直接访问rewards页面...")
            driver.get('https://rewards.bing.com')
            time.sleep(5)
            
            # 尝试多种选择器查找积分任务
            selectors = [
                "div.point_cont",  # 积分容器 - 主要目标
                "div[class*='point_cont']",  # 包含point_cont的元素
                "div.fc_auto.pc.b_subtitle",  # 任务容器
                "div[class*='fc_auto']",  # 自动任务容器
                "div.promo_cont",  # 推广任务容器
                "div[role='banner']",  # 带有role='banner'的元素
                "div[aria-label*='Offer']",  # 包含Offer的aria-label
                "div[class*='rewards']",  # 奖励相关元素
                "div[class*='task']",  # 任务相关元素
                "div[class*='offer']"  # 优惠相关元素
            ]
            
            reward_tasks = []
            for selector in selectors:
                try:
                    tasks = driver.find_elements(By.CSS_SELECTOR, selector)
                    if tasks:
                        print(f"✅ 使用选择器 '{selector}' 找到 {len(tasks)} 个元素")
                        reward_tasks = tasks
                        break
                except:
                    continue
            
            if not reward_tasks:
                # 方法2: 回到必应首页查找积分侧栏
                print("🔄 回到必应首页查找积分侧栏...")
                driver.get('https://cn.bing.com')
                time.sleep(5)
                
                # 尝试查找积分容器
                try:
                    # 尝试多种选择器
                    points_selectors = [
                        "div.b_clickarea",
                        "div[class*='points']",
                        "div[class*='rewards']",
                        "span.points-container",
                        "div[data-tag*='Rewards']"
                    ]
                    
                    points_container = None
                    for selector in points_selectors:
                        try:
                            points_container = driver.find_element(By.CSS_SELECTOR, selector)
                            print(f"✅ 找到积分容器: {selector}")
                            break
                        except:
                            continue
                    
                    if points_container:
                        # 点击积分侧栏
                        driver.execute_script("arguments[0].click();", points_container)
                        time.sleep(3)
                        
                        # 再次尝试查找积分任务
                        for selector in selectors:
                            try:
                                tasks = driver.find_elements(By.CSS_SELECTOR, selector)
                                if tasks:
                                    print(f"✅ 点击后找到 {len(tasks)} 个积分任务")
                                    reward_tasks = tasks
                                    break
                            except:
                                continue
                    else:
                        print("❌ 未找到积分容器")
                        
                except Exception as e:
                    print(f"❌ 查找积分侧栏失败: {e}")
            
            if not reward_tasks:
                # 方法3: 查找并切换到iframe
                print("🔄 尝试查找iframe中的积分任务...")
                try:
                    # 查找iframe
                    iframe_selectors = [
                        "iframe[src*='rewards']",
                        "iframe[src*='panelflyout']",
                        "iframe[src*='bingflyout']",
                        "iframe"
                    ]
                    
                    iframe = None
                    for selector in iframe_selectors:
                        try:
                            iframes = driver.find_elements(By.CSS_SELECTOR, selector)
                            for iframe_elem in iframes:
                                src = iframe_elem.get_attribute('src')
                                if src and ('rewards' in src or 'panelflyout' in src or 'bingflyout' in src):
                                    iframe = iframe_elem
                                    print(f"✅ 找到积分iframe: {src}")
                                    break
                            if iframe:
                                break
                        except:
                            continue
                    
                    if iframe:
                        # 切换到iframe
                        print("🔄 切换到iframe...")
                        driver.switch_to.frame(iframe)
                        time.sleep(3)
                        
                        # 等待iframe内容加载
                        try:
                            from selenium.webdriver.support.ui import WebDriverWait
                            from selenium.webdriver.support import expected_conditions as EC
                            
                            wait = WebDriverWait(driver, 10)
                            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div")))
                        except:
                            print("⚠️ iframe内容加载超时，继续尝试")
                        
                        # 在iframe中查找任务
                        for selector in selectors:
                            try:
                                tasks = driver.find_elements(By.CSS_SELECTOR, selector)
                                if tasks:
                                    print(f"✅ 在iframe中使用选择器 '{selector}' 找到 {len(tasks)} 个任务")
                                    reward_tasks = tasks
                                    break
                            except:
                                continue
                        
                        # 切换回主文档
                        driver.switch_to.default_content()
                        
                        # 如果找到了任务，需要重新切换到iframe进行分析
                        if reward_tasks:
                            print("🔄 重新切换到iframe进行任务分析...")
                            driver.switch_to.frame(iframe)
                            time.sleep(2)
                            
                            # 滚动到iframe底部确保所有任务都加载
                            try:
                                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                                time.sleep(2)
                                driver.execute_script("window.scrollTo(0, 0);")
                                time.sleep(1)
                            except:
                                print("⚠️ iframe滚动失败，继续尝试")
                    else:
                        print("❌ 未找到积分iframe")
                except Exception as e:
                    print(f"⚠️ 处理iframe失败: {str(e)}")
                    try:
                        driver.switch_to.default_content()
                    except:
                        pass
            
            if not reward_tasks:
                print("ℹ️ 没有找到可获得的积分任务")
                driver.quit()
                return
            
            print(f"🎯 找到 {len(reward_tasks)} 个积分任务")
            
                        # 分析每个任务
            for i, task in enumerate(reward_tasks):
                try:
                    print(f"\n--- 任务 {i+1} ---")
                    
                    # 验证任务元素是否仍然有效
                    try:
                        # 尝试获取任务的基本属性来验证元素是否仍然存在
                        task.get_attribute("aria-label")
                    except:
                        print(f"⚠️ 任务 {i+1} 元素已失效，跳过")
                        continue
                    
                    # 滚动到任务元素位置
                    try:
                        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", task)
                        time.sleep(1)  # 等待滚动完成
                    except:
                        print(f"⚠️ 任务 {i+1} 滚动失败，尝试继续")
                    
                    # 等待元素可见和可交互
                    try:
                        from selenium.webdriver.support.ui import WebDriverWait
                        from selenium.webdriver.support import expected_conditions as EC
                        
                        wait = WebDriverWait(driver, 5)
                        wait.until(EC.element_to_be_clickable(task))
                    except:
                        print(f"⚠️ 任务 {i+1} 等待可见超时，尝试继续")
                    
                    # 检查任务是否已完成
                    check_mark = []
                    try:
                        check_mark = task.find_elements(By.CSS_SELECTOR, "svg.checkMark")
                    except:
                        pass
                    
                    # 方法2: 检查父元素是否包含complete类
                    parent_complete = []
                    try:
                        parent_complete = task.find_elements(By.CSS_SELECTOR, "div.complete")
                    except:
                        pass
                    
                    aria_label = ""
                    try:
                        aria_label = task.get_attribute("aria-label")
                    except:
                        pass
                    
                    is_completed = False
                    
                    if check_mark:
                        is_completed = True
                    elif parent_complete:
                        is_completed = True
                    elif aria_label and ("Completed" in aria_label or "添加到帐户" in aria_label):
                        is_completed = True
                    
                    if is_completed:
                        print("✅ 任务已完成")
                        continue
                    
                    # 获取任务名称
                    task_name = "未知任务"
                    try:
                        # 尝试从父元素获取aria-label
                        parent_element = task.find_element(By.XPATH, "./..")
                        parent_aria_label = parent_element.get_attribute("aria-label")
                        
                        if parent_aria_label:
                            if " - " in parent_aria_label:
                                task_name = parent_aria_label.split(" - ")[0]
                            else:
                                task_name = parent_aria_label
                        elif aria_label:
                            if " - " in aria_label:
                                task_name = aria_label.split(" - ")[0]
                            else:
                                task_name = aria_label
                    except:
                        pass
                    print(f"任务名称: {task_name}")
                    
                    # 查找积分数量
                    point_element = None
                    point_selectors = [
                        "div.shortPoint.point",  # 主要目标 - 积分显示元素
                        "div[class*='shortPoint']",  # 包含shortPoint的元素
                        "div[class*='point']",  # 包含point的元素
                        "span[class*='point']",  # span中的积分元素
                        "div[aria-label*='积分']"  # aria-label包含积分的元素
                    ]
                    
                    for selector in point_selectors:
                        try:
                            point_element = task.find_element(By.CSS_SELECTOR, selector)
                            break
                        except:
                            continue
                    
                    if point_element:
                        try:
                            points = point_element.text
                            print(f"积分: {points}")
                        except:
                            print("积分: 无法获取")
                    else:
                        print("积分: 未知")
                    
                    # 获取任务文本
                    try:
                        task_text = task.text
                        print(f"任务内容: {task_text}")
                    except:
                        print("任务内容: 无法获取")
                    
                    # 获取任务HTML
                    try:
                        task_html = task.get_attribute('outerHTML')
                        print(f"HTML: {task_html[:200]}...")
                    except:
                        print("HTML: 无法获取")
                        
                except Exception as e:
                    print(f"⚠️ 分析任务 {i+1} 时出错: {e}")
                    continue
            
        except Exception as e:
            print(f"❌ 积分任务测试失败: {e}")
        
        driver.quit()
        print("🎉 测试完成！")
        
    except Exception as e:
        print(f"❌ 测试出错: {e}")

if __name__ == "__main__":
    test_rewards_task() 