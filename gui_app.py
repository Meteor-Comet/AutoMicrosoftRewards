#!/usr/bin/env python3
"""
Microsoft Rewards 图形化界面工具
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import json
import time
import os
import random
import sys
from datetime import datetime

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

class MicrosoftRewardsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Microsoft Rewards 自动化工具")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # 设置图标和样式
        self.setup_styles()
        
        # 创建主框架
        self.create_widgets()
        
        # 初始化变量
        self.driver = None
        self.is_running = False
        self.current_task = None
        
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 配置样式
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Error.TLabel', foreground='red')
        style.configure('Warning.TLabel', foreground='orange')
        
    def create_widgets(self):
        """创建界面组件"""
        # 主标题
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill='x', padx=10, pady=10)
        
        title_label = ttk.Label(title_frame, text="Microsoft Rewards 自动化工具", style='Title.TLabel')
        title_label.pack()
        
        # 创建选项卡
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 登录选项卡
        self.create_login_tab(notebook)
        
        # 搜索选项卡
        self.create_search_tab(notebook)
        
        # 设置选项卡
        self.create_settings_tab(notebook)
        
        # 日志选项卡
        self.create_log_tab(notebook)
        
    def create_login_tab(self, notebook):
        """创建登录选项卡"""
        login_frame = ttk.Frame(notebook)
        notebook.add(login_frame, text="🔐 登录管理")
        
        # 登录说明
        info_frame = ttk.LabelFrame(login_frame, text="登录说明", padding=10)
        info_frame.pack(fill='x', padx=10, pady=5)
        
        info_text = """
1. 点击"开始登录"按钮
2. 程序会自动打开浏览器并访问必应
3. 在浏览器中手动登录你的Microsoft账户
4. 程序会自动检测登录状态并保存cookies
5. 登录成功后可以关闭浏览器
        """
        info_label = ttk.Label(info_frame, text=info_text, justify='left')
        info_label.pack(anchor='w')
        
        # 登录按钮
        button_frame = ttk.Frame(login_frame)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        self.login_button = ttk.Button(button_frame, text="🔐 开始登录", 
                                      command=self.start_login, style='Accent.TButton')
        self.login_button.pack(side='left', padx=5)
        
        self.stop_login_button = ttk.Button(button_frame, text="⏹️ 停止登录", 
                                           command=self.stop_login, state='disabled')
        self.stop_login_button.pack(side='left', padx=5)
        
        # 状态显示
        status_frame = ttk.LabelFrame(login_frame, text="登录状态", padding=10)
        status_frame.pack(fill='x', padx=10, pady=5)
        
        self.login_status_label = ttk.Label(status_frame, text="等待开始登录...")
        self.login_status_label.pack(anchor='w')
        
    def create_search_tab(self, notebook):
        """创建搜索选项卡"""
        search_frame = ttk.Frame(notebook)
        notebook.add(search_frame, text="🔍 自动搜索")
        
        # 搜索选项
        options_frame = ttk.LabelFrame(search_frame, text="搜索选项", padding=10)
        options_frame.pack(fill='x', padx=10, pady=5)
        
        # 搜索类型选择
        self.search_type = tk.StringVar(value="both")
        ttk.Radiobutton(options_frame, text="🖥️ 桌面端搜索 (30次)", 
                       variable=self.search_type, value="desktop").pack(anchor='w')
        ttk.Radiobutton(options_frame, text="📱 移动端搜索 (20次)", 
                       variable=self.search_type, value="mobile").pack(anchor='w')
        ttk.Radiobutton(options_frame, text="🔄 完整搜索 (桌面+移动)", 
                       variable=self.search_type, value="both").pack(anchor='w')
        
        # 搜索参数
        params_frame = ttk.LabelFrame(search_frame, text="搜索参数", padding=10)
        params_frame.pack(fill='x', padx=10, pady=5)
        
        # 搜索间隔
        interval_frame = ttk.Frame(params_frame)
        interval_frame.pack(fill='x', pady=2)
        ttk.Label(interval_frame, text="搜索间隔 (秒):").pack(side='left')
        self.interval_var = tk.StringVar(value="8")
        interval_entry = ttk.Entry(interval_frame, textvariable=self.interval_var, width=10)
        interval_entry.pack(side='left', padx=5)
        
        # 搜索次数
        count_frame = ttk.Frame(params_frame)
        count_frame.pack(fill='x', pady=2)
        ttk.Label(count_frame, text="桌面端搜索次数:").pack(side='left')
        self.desktop_count_var = tk.StringVar(value="30")
        desktop_count_entry = ttk.Entry(count_frame, textvariable=self.desktop_count_var, width=10)
        desktop_count_entry.pack(side='left', padx=5)
        
        ttk.Label(count_frame, text="移动端搜索次数:").pack(side='left', padx=(20,0))
        self.mobile_count_var = tk.StringVar(value="20")
        mobile_count_entry = ttk.Entry(count_frame, textvariable=self.mobile_count_var, width=10)
        mobile_count_entry.pack(side='left', padx=5)
        
        # 搜索按钮
        button_frame = ttk.Frame(search_frame)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        self.search_button = ttk.Button(button_frame, text="🚀 开始搜索", 
                                       command=self.start_search, style='Accent.TButton')
        self.search_button.pack(side='left', padx=5)
        
        self.stop_search_button = ttk.Button(button_frame, text="⏹️ 停止搜索", 
                                            command=self.stop_search, state='disabled')
        self.stop_search_button.pack(side='left', padx=5)
        
        # 进度显示
        progress_frame = ttk.LabelFrame(search_frame, text="搜索进度", padding=10)
        progress_frame.pack(fill='x', padx=10, pady=5)
        
        self.progress_var = tk.StringVar(value="等待开始搜索...")
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.pack(anchor='w')
        
        # 进度条
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.pack(fill='x', pady=5)
        
    def create_settings_tab(self, notebook):
        """创建设置选项卡"""
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="⚙️ 设置")
        
        # 文件检查
        files_frame = ttk.LabelFrame(settings_frame, text="文件检查", padding=10)
        files_frame.pack(fill='x', padx=10, pady=5)
        
        self.check_files_button = ttk.Button(files_frame, text="🔍 检查必要文件", 
                                            command=self.check_files)
        self.check_files_button.pack(side='left', padx=5)
        
        self.files_status_label = ttk.Label(files_frame, text="点击按钮检查文件状态")
        self.files_status_label.pack(side='left', padx=10)
        
        # Cookies管理
        cookies_frame = ttk.LabelFrame(settings_frame, text="Cookies管理", padding=10)
        cookies_frame.pack(fill='x', padx=10, pady=5)
        
        self.validate_cookies_button = ttk.Button(cookies_frame, text="🔍 验证Cookies", 
                                                 command=self.validate_cookies)
        self.validate_cookies_button.pack(side='left', padx=5)
        
        self.delete_cookies_button = ttk.Button(cookies_frame, text="🗑️ 删除Cookies", 
                                              command=self.delete_cookies)
        self.delete_cookies_button.pack(side='left', padx=5)
        
        self.cookies_status_label = ttk.Label(cookies_frame, text="")
        self.cookies_status_label.pack(side='left', padx=10)
        
        # 搜索词管理
        terms_frame = ttk.LabelFrame(settings_frame, text="搜索词管理", padding=10)
        terms_frame.pack(fill='x', padx=10, pady=5)
        
        self.edit_terms_button = ttk.Button(terms_frame, text="✏️ 编辑搜索词", 
                                           command=self.edit_search_terms)
        self.edit_terms_button.pack(side='left', padx=5)
        
        self.terms_status_label = ttk.Label(terms_frame, text="")
        self.terms_status_label.pack(side='left', padx=10)
        
    def create_log_tab(self, notebook):
        """创建日志选项卡"""
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text="📋 运行日志")
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, width=80)
        self.log_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 日志控制按钮
        log_control_frame = ttk.Frame(log_frame)
        log_control_frame.pack(fill='x', padx=10, pady=5)
        
        self.clear_log_button = ttk.Button(log_control_frame, text="🗑️ 清空日志", 
                                          command=self.clear_log)
        self.clear_log_button.pack(side='left', padx=5)
        
        self.save_log_button = ttk.Button(log_control_frame, text="💾 保存日志", 
                                         command=self.save_log)
        self.save_log_button.pack(side='left', padx=5)
        
    def log_message(self, message, level="INFO"):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        level_icons = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARNING": "⚠️"}
        icon = level_icons.get(level, "ℹ️")
        
        log_entry = f"[{timestamp}] {icon} {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
        # 更新状态标签
        if level == "SUCCESS":
            self.update_status(f"✅ {message}", "success")
        elif level == "ERROR":
            self.update_status(f"❌ {message}", "error")
        elif level == "WARNING":
            self.update_status(f"⚠️ {message}", "warning")
        else:
            self.update_status(f"ℹ️ {message}", "info")
    
    def update_status(self, message, status_type="info"):
        """更新状态显示"""
        if hasattr(self, 'login_status_label'):
            self.login_status_label.config(text=message)
        if hasattr(self, 'progress_var'):
            self.progress_var.set(message)
    
    def check_files(self):
        """检查必要文件"""
        self.log_message("开始检查必要文件...")
        
        missing_files = []
        
        # 检查ChromeDriver
        if not os.path.exists("chromedriver.exe"):
            missing_files.append("chromedriver.exe")
        else:
            self.log_message("✅ ChromeDriver存在", "SUCCESS")
        
        # 检查cookies文件
        if not os.path.exists("cookies.txt"):
            missing_files.append("cookies.txt")
            self.log_message("⚠️ cookies.txt不存在，需要先登录", "WARNING")
        else:
            self.log_message("✅ cookies.txt存在", "SUCCESS")
        
        # 检查自定义搜索词文件
        if not os.path.exists("custom_search_terms.py"):
            self.log_message("ℹ️ 使用默认搜索词列表", "INFO")
        else:
            self.log_message("✅ 自定义搜索词文件存在", "SUCCESS")
        
        if missing_files:
            self.files_status_label.config(text=f"缺少文件: {', '.join(missing_files)}")
            self.log_message(f"❌ 缺少必要文件: {', '.join(missing_files)}", "ERROR")
        else:
            self.files_status_label.config(text="所有文件正常")
            self.log_message("✅ 所有必要文件检查通过", "SUCCESS")
    
    def validate_cookies(self):
        """验证cookies"""
        if not os.path.exists("cookies.txt"):
            self.log_message("❌ cookies.txt文件不存在", "ERROR")
            return
        
        try:
            with open("cookies.txt", 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            self.log_message(f"📂 发现 {len(cookies)} 个cookies")
            
            valid_count = 0
            for cookie in cookies:
                if cookie.get('name') and cookie.get('value'):
                    valid_count += 1
            
            if valid_count == len(cookies):
                self.cookies_status_label.config(text=f"✅ {valid_count}个有效cookies")
                self.log_message(f"✅ 所有 {valid_count} 个cookies都有效", "SUCCESS")
            else:
                self.cookies_status_label.config(text=f"⚠️ {valid_count}/{len(cookies)}个有效")
                self.log_message(f"⚠️ {valid_count}/{len(cookies)} 个cookies有效", "WARNING")
                
        except Exception as e:
            self.log_message(f"❌ 验证cookies时出错: {e}", "ERROR")
    
    def delete_cookies(self):
        """删除cookies文件"""
        if os.path.exists("cookies.txt"):
            try:
                os.remove("cookies.txt")
                self.cookies_status_label.config(text="🗑️ cookies已删除")
                self.log_message("✅ cookies文件已删除", "SUCCESS")
            except Exception as e:
                self.log_message(f"❌ 删除cookies时出错: {e}", "ERROR")
        else:
            self.log_message("ℹ️ cookies文件不存在", "INFO")
    
    def edit_search_terms(self):
        """编辑搜索词"""
        try:
            if os.name == 'nt':  # Windows
                os.system("notepad custom_search_terms.py")
            else:  # Linux/Mac
                os.system("nano custom_search_terms.py")
            self.log_message("📝 已打开搜索词编辑窗口", "INFO")
        except Exception as e:
            self.log_message(f"❌ 打开编辑器时出错: {e}", "ERROR")
    
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("🗑️ 日志已清空", "INFO")
    
    def save_log(self):
        """保存日志"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"log_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.log_text.get(1.0, tk.END))
            
            self.log_message(f"💾 日志已保存到 {filename}", "SUCCESS")
        except Exception as e:
            self.log_message(f"❌ 保存日志时出错: {e}", "ERROR")
    
    def start_login(self):
        """开始登录"""
        if self.is_running:
            return
        
        self.is_running = True
        self.login_button.config(state='disabled')
        self.stop_login_button.config(state='normal')
        
        # 在新线程中执行登录
        self.login_thread = threading.Thread(target=self.login_worker)
        self.login_thread.daemon = True
        self.login_thread.start()
    
    def login_worker(self):
        """登录工作线程"""
        try:
            self.log_message("🚀 开始登录流程...")
            self.update_status("正在初始化浏览器...")
            
            # 设置Chrome选项
            options = webdriver.ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("--mute-audio")
            
            # 初始化驱动
            chromedriver_path = "./chromedriver.exe"
            service = Service(executable_path=chromedriver_path)
            
            self.driver = webdriver.Chrome(service=service, options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.driver.maximize_window()
            
            self.log_message("✅ 浏览器初始化成功", "SUCCESS")
            self.update_status("正在访问必应...")
            
            # 访问必应
            self.driver.get('https://cn.bing.com')
            time.sleep(3)
            
            self.log_message("🌐 已访问必应首页", "SUCCESS")
            self.update_status("请在浏览器中手动登录，程序会自动检测登录状态...")
            
            # 开始检测登录状态
            max_wait_time = 300  # 5分钟
            check_interval = 5  # 每5秒检查一次
            elapsed_time = 0
            
            while elapsed_time < max_wait_time and self.is_running:
                try:
                    current_url = self.driver.current_url
                    
                    # 检查是否在登录页面
                    if "login" in current_url.lower() or "account" in current_url.lower():
                        self.log_message("⏳ 当前在登录页面，等待登录完成...")
                        time.sleep(check_interval)
                        elapsed_time += check_interval
                        continue
                    
                    # 检查是否在必应首页
                    if "bing.com" in current_url and "login" not in current_url.lower():
                        self.log_message("✅ 当前在必应首页")
                        
                        # 检查用户元素
                        try:
                            user_elements = self.driver.find_elements(By.CSS_SELECTOR,
                                "[data-testid='user-avatar'], .user-avatar, .user-name, [aria-label*='用户'], [aria-label*='User'], .user-info")
                            if user_elements:
                                self.log_message("✅ 检测到用户头像/用户名元素，登录成功！", "SUCCESS")
                                break
                        except:
                            pass
                        
                        # 检查登录按钮
                        try:
                            login_element = self.driver.find_element(By.ID, "id_s")
                            login_text = login_element.text.strip()
                            if login_text != "登录":
                                self.log_message("✅ 登录按钮文本已变化，登录成功！", "SUCCESS")
                                break
                            else:
                                self.log_message("⏳ 登录按钮仍显示'登录'，等待登录...")
                        except NoSuchElementException:
                            # 检查搜索框
                            try:
                                search_box = self.driver.find_element(By.ID, "sb_form_q")
                                self.log_message("✅ 检测到搜索框，可能已登录", "SUCCESS")
                                break
                            except:
                                pass
                            
                            # 检查账户元素
                            try:
                                account_elements = self.driver.find_elements(By.CSS_SELECTOR,
                                    "[aria-label*='账户'], [aria-label*='Account'], .account-menu, .user-menu")
                                if account_elements:
                                    self.log_message("✅ 检测到账户相关元素，登录成功！", "SUCCESS")
                                    break
                            except:
                                pass
                    
                    time.sleep(check_interval)
                    elapsed_time += check_interval
                    
                except Exception as e:
                    self.log_message(f"⚠️ 检查登录状态时出错: {e}", "WARNING")
                    time.sleep(check_interval)
                    elapsed_time += check_interval
            
            if elapsed_time >= max_wait_time:
                self.log_message("❌ 登录超时，请重试", "ERROR")
                self.update_status("登录超时")
            elif self.is_running:
                # 保存cookies
                self.log_message("💾 正在保存cookies...")
                cookies = self.driver.get_cookies()
                
                with open('cookies.txt', 'w', encoding='utf-8') as f:
                    json.dump(cookies, f, ensure_ascii=False, indent=2)
                
                self.log_message(f"✅ 成功保存 {len(cookies)} 个cookies", "SUCCESS")
                self.update_status("登录成功，cookies已保存")
                
        except Exception as e:
            self.log_message(f"❌ 登录过程中出错: {e}", "ERROR")
            self.update_status("登录失败")
        
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
            
            self.is_running = False
            self.login_button.config(state='normal')
            self.stop_login_button.config(state='disabled')
    
    def stop_login(self):
        """停止登录"""
        self.is_running = False
        self.log_message("⏹️ 用户停止登录", "WARNING")
        self.update_status("登录已停止")
        
        if self.driver:
            self.driver.quit()
            self.driver = None
        
        self.login_button.config(state='normal')
        self.stop_login_button.config(state='disabled')
    
    def start_search(self):
        """开始搜索"""
        if self.is_running:
            return
        
        # 检查cookies
        if not os.path.exists("cookies.txt"):
            messagebox.showerror("错误", "请先登录获取cookies！")
            return
        
        self.is_running = True
        self.search_button.config(state='disabled')
        self.stop_search_button.config(state='normal')
        
        # 获取搜索参数
        search_type = self.search_type.get()
        interval = int(self.interval_var.get())
        desktop_count = int(self.desktop_count_var.get())
        mobile_count = int(self.mobile_count_var.get())
        
        # 在新线程中执行搜索
        self.search_thread = threading.Thread(target=self.search_worker, 
                                           args=(search_type, interval, desktop_count, mobile_count))
        self.search_thread.daemon = True
        self.search_thread.start()
    
    def search_worker(self, search_type, interval, desktop_count, mobile_count):
        """搜索工作线程"""
        try:
            self.log_message(f"🚀 开始搜索任务: {search_type}")
            
            if search_type in ["desktop", "both"]:
                self.log_message("🖥️ 开始桌面端搜索...")
                if not self.desktop_search_worker(desktop_count, interval):
                    self.log_message("❌ 桌面端搜索失败", "ERROR")
                    return
            
            if search_type in ["mobile", "both"]:
                self.log_message("📱 开始移动端搜索...")
                if not self.mobile_search_worker(mobile_count, interval):
                    self.log_message("❌ 移动端搜索失败", "ERROR")
                    return
            
            self.log_message("🎉 搜索任务完成！", "SUCCESS")
            self.update_status("搜索完成")
            
        except Exception as e:
            self.log_message(f"❌ 搜索过程中出错: {e}", "ERROR")
        finally:
            self.is_running = False
            self.search_button.config(state='normal')
            self.stop_search_button.config(state='disabled')
    
    def desktop_search_worker(self, count, interval):
        """桌面端搜索工作函数"""
        try:
            # 设置Chrome选项
            options = webdriver.ChromeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            options.add_argument("--mute-audio")
            
            # 初始化驱动
            chromedriver_path = "./chromedriver.exe"
            service = Service(executable_path=chromedriver_path)
            
            driver = webdriver.Chrome(service=service, options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            driver.maximize_window()
            
            # 加载cookies
            if not self.load_cookies_worker(driver):
                self.log_message("⚠️ Cookies加载失败，但继续尝试搜索...", "WARNING")
            
            driver.refresh()
            time.sleep(3)
            
            # 执行搜索
            for i in range(count):
                if not self.is_running:
                    break
                
                try:
                    search_box = driver.find_element(By.ID, "sb_form_q")
                    search_box.clear()
                    search_term = random.choice(RANDOM_SEARCH_TERMS)
                    search_box.send_keys(search_term)
                    time.sleep(1)
                    search_box.send_keys(Keys.RETURN)
                    
                    self.log_message(f"🖥️ 桌面搜索 {i+1}/{count}: '{search_term}'")
                    self.update_progress(i+1, count, "桌面端")
                    
                    time.sleep(interval)
                except Exception as e:
                    self.log_message(f"⚠️ 第{i+1}次搜索出错: {e}", "WARNING")
                    driver.get('https://cn.bing.com')
                    time.sleep(3)
                    continue
            
            driver.quit()
            return True
            
        except Exception as e:
            self.log_message(f"❌ 桌面端搜索出错: {e}", "ERROR")
            return False
    
    def mobile_search_worker(self, count, interval):
        """移动端搜索工作函数"""
        try:
            # 设置移动端Chrome选项
            options = webdriver.ChromeOptions()
            options.add_experimental_option('mobileEmulation', {'deviceName': 'Galaxy S5'})
            options.add_argument("--mute-audio")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            # 初始化驱动
            chromedriver_path = "./chromedriver.exe"
            service = Service(executable_path=chromedriver_path)
            
            driver = webdriver.Chrome(service=service, options=options)
            driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # 加载cookies
            if not self.load_cookies_worker(driver):
                self.log_message("⚠️ Cookies加载失败，但继续尝试搜索...", "WARNING")
            
            driver.refresh()
            time.sleep(3)
            
            # 执行搜索
            for i in range(count):
                if not self.is_running:
                    break
                
                try:
                    search_box = driver.find_element(By.ID, "sb_form_q")
                    search_box.clear()
                    search_term = random.choice(RANDOM_SEARCH_TERMS)
                    search_box.send_keys(search_term)
                    time.sleep(1)
                    search_box.send_keys(Keys.RETURN)
                    
                    self.log_message(f"📱 移动搜索 {i+1}/{count}: '{search_term}'")
                    self.update_progress(i+1, count, "移动端")
                    
                    time.sleep(interval)
                except Exception as e:
                    self.log_message(f"⚠️ 第{i+1}次移动搜索出错: {e}", "WARNING")
                    driver.get('https://cn.bing.com')
                    time.sleep(3)
                    continue
            
            driver.quit()
            return True
            
        except Exception as e:
            self.log_message(f"❌ 移动端搜索出错: {e}", "ERROR")
            return False
    
    def load_cookies_worker(self, driver):
        """加载cookies工作函数"""
        try:
            with open('cookies.txt', 'r', encoding='utf-8') as f:
                cookies_list = json.load(f)
            
            self.log_message(f"📂 加载了 {len(cookies_list)} 个cookies")
            
            # 先访问必应网站
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
                    self.log_message(f"⚠️ 跳过无效cookie: {cookie.get('name', 'unknown')} - {str(e)}", "WARNING")
                    invalid_cookies += 1
                    continue
            
            self.log_message(f"✅ 成功加载 {valid_cookies} 个cookies")
            if invalid_cookies > 0:
                self.log_message(f"⚠️ 跳过了 {invalid_cookies} 个无效cookies", "WARNING")
            
            return valid_cookies > 0
            
        except Exception as e:
            self.log_message(f"❌ 加载cookies时出错: {e}", "ERROR")
            return False
    
    def update_progress(self, current, total, search_type):
        """更新进度条"""
        progress = (current / total) * 100
        self.progress_bar['value'] = progress
        self.progress_var.set(f"{search_type}搜索进度: {current}/{total} ({progress:.1f}%)")
    
    def stop_search(self):
        """停止搜索"""
        self.is_running = False
        self.log_message("⏹️ 用户停止搜索", "WARNING")
        self.update_status("搜索已停止")
        
        self.search_button.config(state='normal')
        self.stop_search_button.config(state='disabled')
        self.progress_bar['value'] = 0

def main():
    """主函数"""
    root = tk.Tk()
    app = MicrosoftRewardsGUI(root)
    
    # 设置窗口关闭事件
    def on_closing():
        if app.is_running:
            if messagebox.askokcancel("退出", "程序正在运行中，确定要退出吗？"):
                app.is_running = False
                root.destroy()
        else:
            root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # 启动GUI
    root.mainloop()

if __name__ == "__main__":
    main() 