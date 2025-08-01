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
import webbrowser

# 尝试导入可选模块
try:
    from account_manager import AccountManager
    ACCOUNT_MANAGER_AVAILABLE = True
except ImportError:
    ACCOUNT_MANAGER_AVAILABLE = False
    print("警告: account_manager 模块不可用")

try:
    from chromedriver_updater import ChromeDriverUpdater
    CHROMEDRIVER_UPDATER_AVAILABLE = True
except ImportError:
    CHROMEDRIVER_UPDATER_AVAILABLE = False
    print("警告: chromedriver_updater 模块不可用")

try:
    from config_manager import ConfigManager
    CONFIG_MANAGER_AVAILABLE = True
except ImportError:
    CONFIG_MANAGER_AVAILABLE = False
    print("警告: config_manager 模块不可用")

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
        
        # 初始化配置管理器
        if CONFIG_MANAGER_AVAILABLE:
            self.config_manager = ConfigManager()
        else:
            self.config_manager = None
        
        # 初始化账号管理器
        if ACCOUNT_MANAGER_AVAILABLE:
            self.account_manager = AccountManager()
        else:
            self.account_manager = None
        
        # 设置样式
        self.setup_styles()
        
        # 创建界面
        self.create_widgets()
        
        # 加载保存的设置
        self.load_saved_settings()
        
        # 搜索状态
        self.is_running = False
    
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        
        # 配置主题
        style.theme_use('clam')
        
        # 配置按钮样式
        style.configure('Accent.TButton', 
                       background='#0078d4', 
                       foreground='white',
                       font=('Arial', 9, 'bold'))
        
        # 配置标签样式
        style.configure('Title.TLabel', 
                       font=('Arial', 12, 'bold'),
                       foreground='#0078d4')
        
        # 配置进度条样式
        style.configure("Horizontal.TProgressbar", 
                       background='#0078d4',
                       troughcolor='#f0f0f0')

    def load_saved_settings(self):
        """加载保存的设置"""
        if not self.config_manager:
            return
        
        try:
            # 加载搜索设置
            search_settings = self.config_manager.get_search_settings()
            
            # 设置搜索参数
            if hasattr(self, 'interval_var'):
                self.interval_var.set(search_settings.get('interval', '8'))
            if hasattr(self, 'desktop_count_var'):
                self.desktop_count_var.set(search_settings.get('desktop_count', '30'))
            if hasattr(self, 'mobile_count_var'):
                self.mobile_count_var.set(search_settings.get('mobile_count', '20'))
            if hasattr(self, 'search_type'):
                self.search_type.set(search_settings.get('search_type', 'both'))
            
            # 加载窗口几何信息
            geometry = self.config_manager.get_window_geometry()
            if geometry:
                self.root.geometry(geometry)
            
            # 加载上次使用的账号
            last_account = self.config_manager.get_last_account()
            if last_account and self.account_manager:
                # 尝试切换到上次使用的账号
                try:
                    self.account_manager.switch_to_account(last_account)
                    self.log_message(f"已切换到上次使用的账号: {last_account}")
                except:
                    pass
            
            self.log_message("✅ 已加载保存的设置")
            
        except Exception as e:
            self.log_message(f"❌ 加载设置时出错: {str(e)}")

    def save_current_settings(self):
        """保存当前设置"""
        if not self.config_manager:
            return False
        
        try:
            # 保存搜索设置
            interval = self.interval_var.get() if hasattr(self, 'interval_var') else '8'
            desktop_count = self.desktop_count_var.get() if hasattr(self, 'desktop_count_var') else '30'
            mobile_count = self.mobile_count_var.get() if hasattr(self, 'mobile_count_var') else '20'
            search_type = self.search_type.get() if hasattr(self, 'search_type') else 'both'
            
            success = self.config_manager.save_search_settings(
                interval, desktop_count, mobile_count, search_type
            )
            
            if success:
                self.log_message("✅ 设置已保存")
                return True
            else:
                self.log_message("❌ 保存设置失败")
                return False
                
        except Exception as e:
            self.log_message(f"❌ 保存设置时出错: {str(e)}")
            return False
    
    def create_widgets(self):
        """创建界面组件"""
        # 主标题
        title_frame = ttk.Frame(self.root)
        title_frame.pack(fill='x', padx=10, pady=10)
        
        title_label = ttk.Label(title_frame, text="Microsoft Rewards 自动化工具", style='Title.TLabel')
        title_label.pack()
        
        # 创建选项卡
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=(5, 0))
        
        # 账号管理选项卡
        self.create_account_tab(notebook)
        
        # 登录选项卡
        self.create_login_tab(notebook)
        
        # 搜索选项卡
        self.create_search_tab(notebook)
        
        # 设置选项卡
        self.create_settings_tab(notebook)
        
        # 日志选项卡
        self.create_log_tab(notebook)
        
        # 创建底部信息栏
        self.create_footer()
        
    def create_footer(self):
        """创建底部信息栏"""
        footer_frame = ttk.Frame(self.root)
        footer_frame.pack(fill='x', padx=10, pady=(5, 10))
        
        # 分隔线
        separator = ttk.Separator(footer_frame, orient='horizontal')
        separator.pack(fill='x', pady=(0, 5))
        
        # 项目信息
        info_frame = ttk.Frame(footer_frame)
        info_frame.pack(fill='x')
        
        # 左侧：版本信息
        version_label = ttk.Label(info_frame, text="Microsoft Rewards 自动化工具 v2.2", 
                                 font=('Arial', 9), foreground='gray')
        version_label.pack(side='left')
        
        # 右侧：项目链接
        link_frame = ttk.Frame(info_frame)
        link_frame.pack(side='right')
        
        # GitHub链接
        github_label = ttk.Label(link_frame, text="GitHub: ", font=('Arial', 9), foreground='gray')
        github_label.pack(side='left')
        
        # 创建可点击的链接
        link_label = ttk.Label(link_frame, text="https://github.com/Meteor-Comet/AutoMicrosoftRewards", 
                              font=('Arial', 9), foreground='blue', cursor='hand2')
        link_label.pack(side='left')
        
        # 绑定点击事件
        def open_github(event):
            import webbrowser
            webbrowser.open("https://github.com/Meteor-Comet/AutoMicrosoftRewards")
        
        link_label.bind('<Button-1>', open_github)
        link_label.bind('<Enter>', lambda e: link_label.configure(foreground='darkblue'))
        link_label.bind('<Leave>', lambda e: link_label.configure(foreground='blue'))
        
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
        
        self.relogin_button = ttk.Button(button_frame, text="🔄 重新登录", 
                                        command=self.relogin_current_account)
        self.relogin_button.pack(side='left', padx=5)
        
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
        ttk.Radiobutton(options_frame, text="🎯 积分任务 (点击侧栏任务)", 
                       variable=self.search_type, value="rewards").pack(anchor='w')
        ttk.Radiobutton(options_frame, text="👥 全部账号任务 (所有账号)", 
                       variable=self.search_type, value="all_accounts").pack(anchor='w')
        
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
        
        # 设置保存按钮
        settings_frame = ttk.Frame(params_frame)
        settings_frame.pack(fill='x', pady=(10,0))
        
        self.save_settings_button = ttk.Button(settings_frame, text="💾 保存设置", 
                                             command=self.save_current_settings)
        self.save_settings_button.pack(side='left')
        
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
        
        # 账号管理
        account_settings_frame = ttk.LabelFrame(settings_frame, text="账号管理", padding=10)
        account_settings_frame.pack(fill='x', padx=10, pady=5)
        
        self.refresh_accounts_button = ttk.Button(account_settings_frame, text="🔄 刷新账号列表", 
                                                 command=self.refresh_account_list)
        self.refresh_accounts_button.pack(side='left', padx=5)
        
        self.validate_all_cookies_button = ttk.Button(account_settings_frame, text="🔍 验证所有Cookies", 
                                                     command=self.validate_all_cookies)
        self.validate_all_cookies_button.pack(side='left', padx=5)
        
        # ChromeDriver更新
        chromedriver_frame = ttk.LabelFrame(settings_frame, text="ChromeDriver更新", padding=10)
        chromedriver_frame.pack(fill='x', padx=10, pady=5)
        
        self.check_chromedriver_button = ttk.Button(chromedriver_frame, text="🔍 检查ChromeDriver更新", 
                                                   command=self.check_chromedriver_update)
        self.check_chromedriver_button.pack(side='left', padx=5)
        
        self.update_chromedriver_button = ttk.Button(chromedriver_frame, text="⬇️ 更新ChromeDriver",
                                                   command=self.update_chromedriver)
        self.update_chromedriver_button.pack(side='left', padx=5)

        self.force_update_chromedriver_button = ttk.Button(chromedriver_frame, text="🔄 强制更新",
                                                         command=self.force_update_chromedriver)
        self.force_update_chromedriver_button.pack(side='left', padx=5)

        self.chromedriver_status_label = ttk.Label(chromedriver_frame, text="点击按钮检查ChromeDriver状态")
        self.chromedriver_status_label.pack(side='left', padx=10)
        
    def create_account_tab(self, notebook):
        """创建账号管理选项卡"""
        account_frame = ttk.Frame(notebook)
        notebook.add(account_frame, text="👤 账号管理")
        
        # 账号列表框架
        list_frame = ttk.LabelFrame(account_frame, text="账号列表", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # 创建Treeview用于显示账号列表
        columns = ('账号名称', '状态', '操作')
        self.account_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=8)
        
        # 设置列标题和宽度
        self.account_tree.heading('账号名称', text='账号名称')
        self.account_tree.heading('状态', text='状态')
        self.account_tree.heading('操作', text='操作')
        
        self.account_tree.column('账号名称', width=200, anchor='w')
        self.account_tree.column('状态', width=100, anchor='center')
        self.account_tree.column('操作', width=150, anchor='center')
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.account_tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.account_tree.configure(yscrollcommand=scrollbar.set)
        self.account_tree.pack(fill='both', expand=True, side='left')
        
        # 绑定点击事件
        self.account_tree.bind('<Button-1>', self.on_account_click)
        self.account_tree.bind('<Double-1>', self.on_account_double_click)
        
        # 账号操作按钮
        account_buttons_frame = ttk.Frame(account_frame)
        account_buttons_frame.pack(fill='x', padx=10, pady=5)
        
        self.add_account_button = ttk.Button(account_buttons_frame, text="➕ 添加账号", 
                                           command=self.add_account_dialog)
        self.add_account_button.pack(side='left', padx=5)
        
        self.remove_account_button = ttk.Button(account_buttons_frame, text="🗑️ 删除账号", 
                                              command=self.remove_account)
        self.remove_account_button.pack(side='left', padx=5)
        
        self.save_cookies_button = ttk.Button(account_buttons_frame, text="💾 保存Cookies", 
                                             command=self.save_cookies)
        self.save_cookies_button.pack(side='left', padx=5)
        
        # 当前账号信息
        current_frame = ttk.LabelFrame(account_frame, text="当前账号", padding=10)
        current_frame.pack(fill='x', padx=10, pady=5)
        
        self.current_account_label = ttk.Label(current_frame, text="未选择账号")
        self.current_account_label.pack(anchor='w')
        
        # 刷新账号列表
        self.refresh_account_list()
    
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
                
                # 自动保存到当前账号
                current_account = self.account_manager.get_current_account_name()
                if current_account:
                    success, message = self.account_manager.save_current_cookies(current_account)
                    if success:
                        self.log_message(f"✅ {message}", "SUCCESS")
                    else:
                        self.log_message(f"⚠️ 保存到账号失败: {message}", "WARNING")
                else:
                    self.log_message("ℹ️ 未选择账号，cookies仅保存到临时文件", "INFO")
                
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
            messagebox.showwarning("警告", "搜索正在进行中，请先停止当前搜索")
            return
        
        # 自动保存当前设置
        self.save_current_settings()
        
        # 验证cookies
        if not self.validate_current_cookies():
            return
        
        # 获取搜索参数
        try:
            interval = int(self.interval_var.get())
            desktop_count = int(self.desktop_count_var.get())
            mobile_count = int(self.mobile_count_var.get())
            search_type = self.search_type.get()
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            return
        
        if interval < 1 or desktop_count < 1 or mobile_count < 1:
            messagebox.showerror("错误", "搜索间隔和次数必须大于0")
            return
        
        # 开始搜索
        self.is_running = True
        self.search_button.config(state='disabled')
        self.stop_search_button.config(state='normal')
        
        # 在新线程中运行搜索
        threading.Thread(target=self.search_worker, 
                       args=(search_type, interval, desktop_count, mobile_count),
                       daemon=True).start()
    
    def validate_current_cookies(self):
        """验证当前cookies是否有效"""
        try:
            with open('cookies.txt', 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            if not cookies:
                return False
            
            # 检查是否有必要的cookies
            required_cookies = ['WLSSC', 'MUID', 'SRCHD', 'SRCHUID']
            found_cookies = [cookie.get('name') for cookie in cookies]
            
            # 至少要有一些基本的cookies
            return len(cookies) >= 5
        except Exception:
            return False
    
    def handle_no_cookies(self):
        """处理没有cookies的情况"""
        current_account = self.account_manager.get_current_account_name()
        
        if current_account:
            # 有当前账号，询问是否重新登录
            result = messagebox.askyesnocancel(
                "Cookies不存在", 
                f"当前账号 '{current_account}' 没有登录信息。\n\n"
                "选择操作：\n"
                "• 是(Y): 重新登录获取cookies\n"
                "• 否(N): 切换到其他账号\n"
                "• 取消: 取消操作"
            )
            
            if result is True:  # 重新登录
                self.log_message("🔄 开始重新登录获取cookies...", "INFO")
                self.start_login()
            elif result is False:  # 切换账号
                self.switch_account_dialog()
        else:
            # 没有当前账号，询问是否添加新账号
            result = messagebox.askyesno(
                "Cookies不存在", 
                "没有找到登录信息。\n\n"
                "选择操作：\n"
                "• 是(Y): 添加新账号并登录\n"
                "• 否(N): 取消操作"
            )
            
            if result:
                self.add_account_and_login()
    
    def handle_invalid_cookies(self):
        """处理cookies无效的情况"""
        current_account = self.account_manager.get_current_account_name()
        
        if current_account:
            # 有当前账号，询问如何处理
            result = messagebox.askyesnocancel(
                "Cookies已过期", 
                f"当前账号 '{current_account}' 的登录信息已过期。\n\n"
                "选择操作：\n"
                "• 是(Y): 重新登录获取cookies\n"
                "• 否(N): 切换到其他账号\n"
                "• 取消: 取消操作"
            )
            
            if result is True:  # 重新登录
                self.log_message("🔄 开始重新登录获取cookies...", "INFO")
                self.start_login()
            elif result is False:  # 切换账号
                self.switch_account_dialog()
        else:
            # 没有当前账号，询问是否添加新账号
            result = messagebox.askyesno(
                "Cookies已过期", 
                "登录信息已过期。\n\n"
                "选择操作：\n"
                "• 是(Y): 添加新账号并登录\n"
                "• 否(N): 取消操作"
            )
            
            if result:
                self.add_account_and_login()
    
    def switch_account_dialog(self):
        """账号切换对话框"""
        accounts = self.account_manager.get_account_list()
        
        if not accounts:
            messagebox.showinfo("提示", "没有其他账号可切换，请添加新账号。")
            self.add_account_and_login()
            return
        
        # 创建选择对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("选择账号")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # 居中显示
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 150, self.root.winfo_rooty() + 150))
        
        # 主框架
        main_frame = ttk.Frame(dialog, padding=20)
        main_frame.pack(fill='both', expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="选择要切换的账号", font=('Arial', 12, 'bold'))
        title_label.pack(pady=(0, 15))
        
        # 账号列表
        list_frame = ttk.Frame(main_frame)
        list_frame.pack(fill='both', expand=True, pady=10)
        
        # 创建列表框
        account_listbox = tk.Listbox(list_frame, height=8, font=('Arial', 10))
        account_listbox.pack(fill='both', expand=True, side='left')
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=account_listbox.yview)
        scrollbar.pack(side='right', fill='y')
        account_listbox.configure(yscrollcommand=scrollbar.set)
        
        # 填充账号列表
        for account in accounts:
            status = self.account_manager.get_account_status(account)
            display_text = f"{account} ({status})"
            account_listbox.insert(tk.END, display_text)
        
        def switch_selected_account():
            selection = account_listbox.curselection()
            if not selection:
                messagebox.showwarning("警告", "请先选择一个账号")
                return
            
            account_name = account_listbox.get(selection[0]).split(" (")[0]
            
            # 保存当前cookies（如果有）
            current_account = self.account_manager.get_current_account_name()
            if current_account and os.path.exists("cookies.txt"):
                self.account_manager.save_current_cookies(current_account)
            
            # 切换到新账号
            success, message = self.account_manager.switch_account(account_name)
            
            if success:
                self.log_message(f"✅ {message}", "SUCCESS")
                self.refresh_account_list()
                dialog.destroy()
                
                # 检查新账号是否有cookies
                if not self.account_manager.has_cookies(account_name):
                    result = messagebox.askyesno(
                        "账号未登录", 
                        f"账号 '{account_name}' 还没有登录信息。\n\n是否现在登录？"
                    )
                    if result:
                        self.start_login()
            else:
                messagebox.showerror("错误", message)
        
        def add_new_account():
            dialog.destroy()
            self.add_account_and_login()
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(15, 0))
        
        # 切换按钮
        switch_button = ttk.Button(button_frame, text="切换账号", command=switch_selected_account)
        switch_button.pack(side='left', padx=(0, 10))
        
        # 添加新账号按钮
        add_button = ttk.Button(button_frame, text="添加新账号", command=add_new_account)
        add_button.pack(side='left', padx=(10, 0))
        
        # 取消按钮
        cancel_button = ttk.Button(button_frame, text="取消", command=dialog.destroy)
        cancel_button.pack(side='right')
        
        # 设置焦点
        account_listbox.focus()
        if account_listbox.size() > 0:
            account_listbox.selection_set(0)
    
    def add_account_and_login(self):
        """添加新账号并立即登录"""
        # 先添加账号
        dialog = tk.Toplevel(self.root)
        dialog.title("添加新账号")
        dialog.geometry("550x420")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # 居中显示
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 100))
        
        # 主框架
        main_frame = ttk.Frame(dialog, padding=25)
        main_frame.pack(fill='both', expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="添加新账号并登录", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 25))
        
        # 账号名称
        name_frame = ttk.Frame(main_frame)
        name_frame.pack(fill='x', pady=12)
        ttk.Label(name_frame, text="账号名称 *:", font=('Arial', 11, 'bold')).pack(anchor='w')
        name_var = tk.StringVar()
        name_entry = ttk.Entry(name_frame, textvariable=name_var, width=55, font=('Arial', 10))
        name_entry.pack(fill='x', pady=(8, 0))
        ttk.Label(name_frame, text="必填项，用于标识账号", font=('Arial', 9), foreground='gray').pack(anchor='w')
        
        # 邮箱（可选）
        email_frame = ttk.Frame(main_frame)
        email_frame.pack(fill='x', pady=12)
        ttk.Label(email_frame, text="邮箱地址:", font=('Arial', 11, 'bold')).pack(anchor='w')
        email_var = tk.StringVar()
        email_entry = ttk.Entry(email_frame, textvariable=email_var, width=55, font=('Arial', 10))
        email_entry.pack(fill='x', pady=(8, 0))
        ttk.Label(email_frame, text="可选，用于记录账号邮箱", font=('Arial', 9), foreground='gray').pack(anchor='w')
        
        # 描述（可选）
        desc_frame = ttk.Frame(main_frame)
        desc_frame.pack(fill='x', pady=12)
        ttk.Label(desc_frame, text="账号描述:", font=('Arial', 11, 'bold')).pack(anchor='w')
        desc_var = tk.StringVar()
        desc_entry = ttk.Entry(desc_frame, textvariable=desc_var, width=55, font=('Arial', 10))
        desc_entry.pack(fill='x', pady=(8, 0))
        ttk.Label(desc_frame, text="可选，用于备注账号用途", font=('Arial', 9), foreground='gray').pack(anchor='w')
        
        # 快捷键提示
        hint_frame = ttk.Frame(main_frame)
        hint_frame.pack(fill='x', pady=(15, 0))
        hint_label = ttk.Label(hint_frame, text="💡 提示: 按回车键确定，按ESC键取消", 
                              font=('Arial', 9), foreground='blue')
        hint_label.pack(anchor='center')
        
        # 分隔线
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill='x', pady=25)
        
        def add_and_login():
            account_name = name_var.get().strip()
            if not account_name:
                messagebox.showerror("错误", "请输入账号名称")
                name_entry.focus()
                return
            
            # 检查账号名称是否已存在
            if account_name in self.account_manager.get_account_list():
                messagebox.showerror("错误", "账号名称已存在，请使用其他名称")
                name_entry.focus()
                return
            
            # 添加账号
            success, message = self.account_manager.add_account(
                account_name, 
                email_var.get().strip(), 
                desc_var.get().strip()
            )
            
            if success:
                self.log_message(f"✅ {message}", "SUCCESS")
                self.refresh_account_list()
                dialog.destroy()
                
                # 切换到新账号并开始登录
                self.account_manager.switch_account(account_name)
                self.refresh_account_list()
                self.start_login()
            else:
                messagebox.showerror("错误", message)
        
        def on_enter(event):
            """回车键提交"""
            add_and_login()
        
        def on_escape(event):
            """ESC键取消"""
            dialog.destroy()
        
        # 绑定快捷键
        dialog.bind('<Return>', on_enter)
        dialog.bind('<Escape>', on_escape)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(25, 0))
        
        # 确定按钮
        ok_button = ttk.Button(button_frame, text="添加并登录", command=add_and_login, 
                              style='Accent.TButton', width=15)
        ok_button.pack(side='left', padx=(0, 15))
        
        # 取消按钮
        cancel_button = ttk.Button(button_frame, text="取消", command=dialog.destroy, width=12)
        cancel_button.pack(side='left', padx=(15, 0))
        
        # 设置焦点
        name_entry.focus()
    
    def relogin_current_account(self):
        """重新登录当前账号"""
        current_account = self.account_manager.get_current_account_name()
        
        if not current_account:
            messagebox.showwarning("警告", "没有选择账号，请先在账号管理中切换账号。")
            return
        
        result = messagebox.askyesno(
            "重新登录", 
            f"确定要重新登录账号 '{current_account}' 吗？\n\n"
            "这将覆盖当前的登录信息。"
        )
        
        if result:
            self.log_message(f"🔄 开始重新登录账号 '{current_account}'...", "INFO")
            self.start_login()
    
    def search_worker(self, search_type, interval, desktop_count, mobile_count):
        """搜索工作线程"""
        try:
            self.log_message(f"🚀 开始搜索任务: {search_type}")
            
            # 如果是完整搜索，先执行积分任务
            if search_type == "both":
                self.log_message("🎯 完整搜索模式：先执行积分任务...")
                if not self.rewards_task_worker():
                    self.log_message("⚠️ 积分任务失败，继续执行搜索...", "WARNING")
                else:
                    self.log_message("✅ 积分任务完成，继续执行搜索...")
            
            if search_type in ["desktop", "both"]:
                if desktop_count > 0:
                    self.log_message("🖥️ 开始桌面端搜索...")
                    if not self.desktop_search_worker(desktop_count, interval):
                        self.log_message("❌ 桌面端搜索失败", "ERROR")
                        return
                else:
                    self.log_message("🖥️ 桌面端搜索次数为0，跳过桌面端搜索")
            
            if search_type in ["mobile", "both"]:
                if mobile_count > 0:
                    self.log_message("📱 开始移动端搜索...")
                    if not self.mobile_search_worker(mobile_count, interval):
                        self.log_message("❌ 移动端搜索失败", "ERROR")
                        return
                else:
                    self.log_message("📱 移动端搜索次数为0，跳过移动端搜索")
            
            if search_type == "rewards":
                self.log_message("🎯 开始积分任务...")
                if not self.rewards_task_worker():
                    self.log_message("❌ 积分任务失败", "ERROR")
                    return
            
            if search_type == "all_accounts":
                self.log_message("👥 开始全部账号任务...")
                if not self.all_accounts_worker():
                    self.log_message("❌ 全部账号任务失败", "ERROR")
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
            # 禁用日志输出
            options.add_argument("--log-level=3")
            options.add_argument("--silent")
            
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
    
    def rewards_task_worker(self):
        """积分任务工作函数"""
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
            if not self.load_cookies_worker(driver):
                self.log_message("⚠️ Cookies加载失败，但继续尝试积分任务...", "WARNING")
            
            # 访问必应首页
            driver.get('https://cn.bing.com')
            time.sleep(5)  # 增加等待时间
            
            # 尝试多种方式查找积分侧栏
            self.log_message("🔍 查找积分侧栏...")
            
            # 方法1: 尝试直接访问rewards页面
            try:
                self.log_message("🔄 尝试直接访问rewards页面...")
                driver.get('https://rewards.bing.com')
                time.sleep(5)
                
                # 等待页面加载完成
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                
                wait = WebDriverWait(driver, 10)
                
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
                            self.log_message(f"✅ 使用选择器 '{selector}' 找到 {len(tasks)} 个元素")
                            reward_tasks = tasks
                            break
                    except:
                        continue
                
                if not reward_tasks:
                    # 方法2: 回到必应首页查找积分侧栏
                    self.log_message("🔄 回到必应首页查找积分侧栏...")
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
                                self.log_message(f"✅ 找到积分容器: {selector}")
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
                                        self.log_message(f"✅ 点击后找到 {len(tasks)} 个积分任务")
                                        reward_tasks = tasks
                                        break
                                except:
                                    continue
                        else:
                            self.log_message("❌ 未找到积分容器")
                            
                    except Exception as e:
                        self.log_message(f"❌ 查找积分侧栏失败: {e}", "ERROR")
                
                if not reward_tasks:
                    # 方法3: 查找并切换到iframe
                    self.log_message("🔄 尝试查找iframe中的积分任务...")
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
                                        self.log_message(f"✅ 找到积分iframe: {src}")
                                        break
                                if iframe:
                                    break
                            except:
                                continue
                        
                        if iframe:
                            # 切换到iframe
                            self.log_message("🔄 切换到iframe...")
                            driver.switch_to.frame(iframe)
                            time.sleep(3)
                            
                            # 等待iframe内容加载
                            try:
                                from selenium.webdriver.support.ui import WebDriverWait
                                from selenium.webdriver.support import expected_conditions as EC
                                
                                wait = WebDriverWait(driver, 10)
                                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div")))
                            except:
                                self.log_message("⚠️ iframe内容加载超时，继续尝试")
                            
                            # 在iframe中查找任务
                            for selector in selectors:
                                try:
                                    tasks = driver.find_elements(By.CSS_SELECTOR, selector)
                                    if tasks:
                                        self.log_message(f"✅ 在iframe中使用选择器 '{selector}' 找到 {len(tasks)} 个任务")
                                        reward_tasks = tasks
                                        break
                                except:
                                    continue
                            
                            # 切换回主文档
                            driver.switch_to.default_content()
                            
                            # 如果找到了任务，需要重新切换到iframe进行点击
                            if reward_tasks:
                                self.log_message("🔄 重新切换到iframe进行任务处理...")
                                driver.switch_to.frame(iframe)
                                time.sleep(2)
                                
                                # 滚动到iframe底部确保所有任务都加载
                                try:
                                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                                    time.sleep(2)
                                    driver.execute_script("window.scrollTo(0, 0);")
                                    time.sleep(1)
                                except:
                                    self.log_message("⚠️ iframe滚动失败，继续尝试")
                        else:
                            self.log_message("❌ 未找到积分iframe")
                    except Exception as e:
                        self.log_message(f"⚠️ 处理iframe失败: {str(e)}")
                        # 确保切换回主文档
                        try:
                            driver.switch_to.default_content()
                        except:
                            pass
                
                if not reward_tasks:
                    self.log_message("ℹ️ 没有找到可获得的积分任务", "INFO")
                    driver.quit()
                    return True
                
                completed_tasks = 0
                total_tasks = len(reward_tasks)
                
                # 记录当前是否在iframe中
                in_iframe = False
                if iframe:
                    in_iframe = True
                
                self.log_message(f"🎯 找到 {total_tasks} 个积分任务")
                
                for i, task in enumerate(reward_tasks):
                    if not self.is_running:
                        break
                    
                    try:
                        # 验证任务元素是否仍然有效
                        try:
                            # 尝试获取任务的基本属性来验证元素是否仍然存在
                            task.get_attribute("aria-label")
                        except:
                            self.log_message(f"⚠️ 任务 {i+1}/{total_tasks} 元素已失效，跳过")
                            continue
                        
                        # 滚动到任务元素位置
                        try:
                            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", task)
                            time.sleep(1)  # 等待滚动完成
                        except:
                            self.log_message(f"⚠️ 任务 {i+1}/{total_tasks} 滚动失败，尝试继续")
                        
                        # 等待元素可见和可交互
                        try:
                            from selenium.webdriver.support.ui import WebDriverWait
                            from selenium.webdriver.support import expected_conditions as EC
                            
                            wait = WebDriverWait(driver, 5)
                            wait.until(EC.element_to_be_clickable(task))
                        except:
                            self.log_message(f"⚠️ 任务 {i+1}/{total_tasks} 等待可见超时，尝试继续")
                        
                        # 检查任务是否已完成
                        # 方法1: 查找checkMark图标
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
                        
                        # 方法3: 检查aria-label是否包含"Completed"或"添加到帐户"
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
                            self.log_message(f"✅ 任务 {i+1}/{total_tasks} 已完成，跳过")
                            continue
                        
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
                        
                        if point_element:
                            try:
                                points = point_element.text
                                self.log_message(f"🎯 点击任务 {i+1}/{total_tasks}: {task_name} (积分: {points})")
                            except:
                                self.log_message(f"🎯 点击任务 {i+1}/{total_tasks}: {task_name}")
                        else:
                            self.log_message(f"🎯 点击任务 {i+1}/{total_tasks}: {task_name}")
                        
                        # 验证任务是否仍然可点击
                        try:
                            # 检查任务是否可见和可点击
                            if not task.is_displayed() or not task.is_enabled():
                                self.log_message(f"⚠️ 任务 {i+1}/{total_tasks} 不可点击，跳过")
                                continue
                        except:
                            self.log_message(f"⚠️ 任务 {i+1}/{total_tasks} 状态检查失败，跳过")
                            continue
                        
                        # 使用JavaScript点击任务
                        try:
                            driver.execute_script("arguments[0].click();", task)
                            time.sleep(3)
                        except Exception as e:
                            self.log_message(f"⚠️ 点击任务 {i+1}/{total_tasks} 失败: {e}", "WARNING")
                            continue
                        
                        # 获取所有窗口句柄
                        try:
                            handles = driver.window_handles
                            
                            # 如果有新窗口打开，关闭它
                            if len(handles) > 1:
                                # 切换到新窗口
                                driver.switch_to.window(handles[-1])
                                time.sleep(2)
                                
                                # 关闭新窗口
                                driver.close()
                                
                                # 切换回原窗口
                                driver.switch_to.window(handles[0])
                                
                                # 重新切换到iframe
                                if in_iframe:
                                    try:
                                        driver.switch_to.frame(iframe)
                                        time.sleep(1)
                                    except:
                                        self.log_message(f"⚠️ 任务 {i+1}/{total_tasks} 重新切换iframe失败")
                                
                                self.log_message(f"✅ 任务 {i+1}/{total_tasks} 完成")
                                completed_tasks += 1
                            else:
                                self.log_message(f"⚠️ 任务 {i+1}/{total_tasks} 没有打开新窗口")
                        except Exception as e:
                            self.log_message(f"⚠️ 处理任务窗口失败: {e}", "WARNING")
                            
                            # 确保切换回iframe
                            if in_iframe:
                                try:
                                    driver.switch_to.frame(iframe)
                                    time.sleep(1)
                                except:
                                    self.log_message(f"⚠️ 任务 {i+1}/{total_tasks} 异常后切换iframe失败")
                        
                        self.update_progress(i+1, total_tasks, "积分任务")
                        time.sleep(2)
                        
                    except Exception as e:
                        self.log_message(f"⚠️ 任务 {i+1}/{total_tasks} 出错: {e}", "WARNING")
                        continue
                
                self.log_message(f"🎉 积分任务完成！共完成 {completed_tasks}/{total_tasks} 个任务", "SUCCESS")
                
            except Exception as e:
                self.log_message(f"❌ 积分任务执行失败: {e}", "ERROR")
            finally:
                # 确保切换回主文档
                try:
                    driver.switch_to.default_content()
                except:
                    pass
            
            driver.quit()
            return True
            
        except Exception as e:
            self.log_message(f"❌ 积分任务出错: {e}", "ERROR")
            return False
    
    def all_accounts_worker(self):
        """全部账号任务工作函数"""
        try:
            # 获取所有账号
            accounts = self.account_manager.get_all_accounts()
            if not accounts:
                self.log_message("❌ 没有找到任何账号", "ERROR")
                return False
            
            self.log_message(f"👥 找到 {len(accounts)} 个账号，开始依次处理...")
            
            completed_accounts = 0
            total_accounts = len(accounts)
            
            for i, account_name in enumerate(accounts):
                if not self.is_running:
                    break
                
                self.log_message(f"🔄 处理账号 {i+1}/{total_accounts}: {account_name}")
                
                # 切换到当前账号
                try:
                    self.account_manager.switch_to_account(account_name)
                    self.log_message(f"✅ 已切换到账号: {account_name}")
                except Exception as e:
                    self.log_message(f"❌ 切换账号 {account_name} 失败: {e}", "ERROR")
                    continue
                
                # 为当前账号执行完整搜索任务
                try:
                    # 获取搜索参数
                    interval = float(self.interval_var.get())
                    desktop_count = int(self.desktop_count_var.get())
                    mobile_count = int(self.mobile_count_var.get())
                    
                    self.log_message(f"🎯 开始账号 {account_name} 的完整搜索任务...")
                    
                    # 先执行积分任务
                    self.log_message(f"🎯 账号 {account_name}: 执行积分任务...")
                    if not self.rewards_task_worker():
                        self.log_message(f"⚠️ 账号 {account_name} 积分任务失败，继续...", "WARNING")
                    else:
                        self.log_message(f"✅ 账号 {account_name} 积分任务完成")
                    
                    # 执行桌面端搜索
                    if desktop_count > 0:
                        self.log_message(f"🖥️ 账号 {account_name}: 执行桌面端搜索...")
                        if not self.desktop_search_worker(desktop_count, interval):
                            self.log_message(f"❌ 账号 {account_name} 桌面端搜索失败", "ERROR")
                            continue
                    else:
                        self.log_message(f"🖥️ 账号 {account_name}: 桌面端搜索次数为0，跳过")
                    
                    # 执行移动端搜索
                    if mobile_count > 0:
                        self.log_message(f"📱 账号 {account_name}: 执行移动端搜索...")
                        if not self.mobile_search_worker(mobile_count, interval):
                            self.log_message(f"❌ 账号 {account_name} 移动端搜索失败", "ERROR")
                            continue
                    else:
                        self.log_message(f"📱 账号 {account_name}: 移动端搜索次数为0，跳过")
                    
                    self.log_message(f"✅ 账号 {account_name} 完整搜索任务完成")
                    completed_accounts += 1
                    
                except Exception as e:
                    self.log_message(f"❌ 账号 {account_name} 任务执行失败: {e}", "ERROR")
                    continue
                
                # 更新进度
                self.update_progress(i+1, total_accounts, f"全部账号任务 ({account_name})")
                
                # 账号间等待
                if i < total_accounts - 1:  # 不是最后一个账号
                    self.log_message(f"⏳ 等待 3 秒后处理下一个账号...")
                    time.sleep(3)
            
            self.log_message(f"🎉 全部账号任务完成！成功处理 {completed_accounts}/{total_accounts} 个账号", "SUCCESS")
            return True
            
        except Exception as e:
            self.log_message(f"❌ 全部账号任务出错: {e}", "ERROR")
            return False
    
    def load_cookies_worker(self, driver):
        """加载cookies工作函数"""
        try:
            # 检查当前账号
            current_account = self.account_manager.get_current_account_name()
            self.log_message(f"🔍 当前账号: {current_account}")
            self.log_message(f"📂 从cookies.txt加载cookies")
            
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
    
    def refresh_account_list(self):
        """刷新账号列表"""
        # 清空现有项目
        for item in self.account_tree.get_children():
            self.account_tree.delete(item)
        
        accounts = self.account_manager.get_account_list()
        current_account = self.account_manager.get_current_account_name()
        
        for account in accounts:
            status = self.account_manager.get_account_status(account)
            
            # 判断是否为当前账号
            if account == current_account:
                status_text = f"✅ {status}"
                switch_text = "当前账号"
            else:
                status_text = status
                switch_text = "🔄 切换"
            
            # 插入到Treeview
            self.account_tree.insert('', 'end', values=(account, status_text, switch_text))
        
        # 更新当前账号显示
        if current_account:
            self.current_account_label.config(text=f"当前账号: {current_account}")
        else:
            self.current_account_label.config(text="未选择账号")
    
    def add_account_dialog(self):
        """添加账号对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("添加账号")
        dialog.geometry("550x420")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)
        
        # 居中显示
        dialog.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 100))
        
        # 主框架
        main_frame = ttk.Frame(dialog, padding=25)
        main_frame.pack(fill='both', expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="添加新账号", font=('Arial', 16, 'bold'))
        title_label.pack(pady=(0, 25))
        
        # 账号名称
        name_frame = ttk.Frame(main_frame)
        name_frame.pack(fill='x', pady=12)
        ttk.Label(name_frame, text="账号名称 *:", font=('Arial', 11, 'bold')).pack(anchor='w')
        name_var = tk.StringVar()
        name_entry = ttk.Entry(name_frame, textvariable=name_var, width=55, font=('Arial', 10))
        name_entry.pack(fill='x', pady=(8, 0))
        ttk.Label(name_frame, text="必填项，用于标识账号", font=('Arial', 9), foreground='gray').pack(anchor='w')
        
        # 邮箱（可选）
        email_frame = ttk.Frame(main_frame)
        email_frame.pack(fill='x', pady=12)
        ttk.Label(email_frame, text="邮箱地址:", font=('Arial', 11, 'bold')).pack(anchor='w')
        email_var = tk.StringVar()
        email_entry = ttk.Entry(email_frame, textvariable=email_var, width=55, font=('Arial', 10))
        email_entry.pack(fill='x', pady=(8, 0))
        ttk.Label(email_frame, text="可选，用于记录账号邮箱", font=('Arial', 9), foreground='gray').pack(anchor='w')
        
        # 描述（可选）
        desc_frame = ttk.Frame(main_frame)
        desc_frame.pack(fill='x', pady=12)
        ttk.Label(desc_frame, text="账号描述:", font=('Arial', 11, 'bold')).pack(anchor='w')
        desc_var = tk.StringVar()
        desc_entry = ttk.Entry(desc_frame, textvariable=desc_var, width=55, font=('Arial', 10))
        desc_entry.pack(fill='x', pady=(8, 0))
        ttk.Label(desc_frame, text="可选，用于备注账号用途", font=('Arial', 9), foreground='gray').pack(anchor='w')
        
        # 快捷键提示
        hint_frame = ttk.Frame(main_frame)
        hint_frame.pack(fill='x', pady=(15, 0))
        hint_label = ttk.Label(hint_frame, text="💡 提示: 按回车键确定，按ESC键取消", 
                              font=('Arial', 9), foreground='blue')
        hint_label.pack(anchor='center')
        
        # 分隔线
        separator = ttk.Separator(main_frame, orient='horizontal')
        separator.pack(fill='x', pady=25)
        
        def add_account():
            account_name = name_var.get().strip()
            if not account_name:
                messagebox.showerror("错误", "请输入账号名称")
                name_entry.focus()
                return
            
            # 检查账号名称是否已存在
            if account_name in self.account_manager.get_account_list():
                messagebox.showerror("错误", "账号名称已存在，请使用其他名称")
                name_entry.focus()
                return
            
            success, message = self.account_manager.add_account(
                account_name, 
                email_var.get().strip(), 
                desc_var.get().strip()
            )
            
            if success:
                self.log_message(f"✅ {message}", "SUCCESS")
                self.refresh_account_list()
                dialog.destroy()
            else:
                messagebox.showerror("错误", message)
        
        def on_enter(event):
            """回车键提交"""
            add_account()
        
        def on_escape(event):
            """ESC键取消"""
            dialog.destroy()
        
        # 绑定快捷键
        dialog.bind('<Return>', on_enter)
        dialog.bind('<Escape>', on_escape)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=(25, 0))
        
        # 确定按钮
        ok_button = ttk.Button(button_frame, text="确定", command=add_account, 
                              style='Accent.TButton', width=12)
        ok_button.pack(side='left', padx=(0, 15))
        
        # 取消按钮
        cancel_button = ttk.Button(button_frame, text="取消", command=dialog.destroy, width=12)
        cancel_button.pack(side='left', padx=(15, 0))
        
        # 设置焦点
        name_entry.focus()
        
        # 设置默认按钮
        dialog.bind('<Return>', lambda e: add_account())
    
    def remove_account(self):
        """删除账号"""
        selection = self.account_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要删除的账号")
            return
        
        # 获取选中的账号名称
        item = selection[0]
        account_name = self.account_tree.item(item, 'values')[0]
        
        if messagebox.askyesno("确认删除", f"确定要删除账号 '{account_name}' 吗？\n\n注意：这将删除该账号的所有数据，包括cookies文件。"):
            success, message = self.account_manager.remove_account(account_name)
            
            if success:
                self.log_message(f"✅ {message}", "SUCCESS")
                self.refresh_account_list()
            else:
                messagebox.showerror("错误", message)
    
    def switch_to_account(self, account_name):
        """切换到指定账号"""
        if not self.account_manager:
            self.log_message("❌ 账号管理模块不可用")
            return False
        
        try:
            success, message = self.account_manager.switch_to_account(account_name)
            if success:
                self.log_message(f"✅ 已切换到账号: {account_name}")
                self.refresh_account_list()
                
                # 保存当前账号到配置
                if self.config_manager:
                    self.config_manager.save_last_account(account_name)
                
                return True
            else:
                self.log_message(f"❌ 切换账号失败: {message}")
                return False
        except Exception as e:
            self.log_message(f"❌ 切换账号时出错: {str(e)}")
            return False
    
    def on_account_click(self, event):
        """账号点击事件"""
        region = self.account_tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.account_tree.identify_column(event.x)
            item = self.account_tree.identify_row(event.y)
            
            if item and column == "#3":  # 第三列（操作列）
                values = self.account_tree.item(item, 'values')
                if values and values[2] == "🔄 切换":  # 只有非当前账号才能切换
                    account_name = values[0]
                    self.switch_to_account(account_name)
    
    def on_account_double_click(self, event):
        """账号双击事件"""
        selection = self.account_tree.selection()
        if selection:
            item = selection[0]
            account_name = self.account_tree.item(item, 'values')[0]
            self.switch_to_account(account_name)
    
    def switch_account(self):
        """切换账号（保留原有方法以兼容）"""
        selection = self.account_tree.selection()
        if not selection:
            messagebox.showwarning("警告", "请先选择要切换的账号")
            return
        
        # 获取选中的账号名称
        item = selection[0]
        account_name = self.account_tree.item(item, 'values')[0]
        self.switch_to_account(account_name)
    
    def save_cookies(self):
        """保存当前cookies到当前账号"""
        current_account = self.account_manager.get_current_account_name()
        if not current_account:
            messagebox.showwarning("警告", "请先选择或登录一个账号")
            return
        
        if not os.path.exists("cookies.txt"):
            messagebox.showwarning("警告", "当前没有cookies文件，请先登录")
            return
        
        success, message = self.account_manager.save_current_cookies(current_account)
        
        if success:
            self.log_message(f"✅ {message}", "SUCCESS")
            self.refresh_account_list()
        else:
            messagebox.showerror("错误", message)
    
    def validate_all_cookies(self):
        """验证所有账号的cookies"""
        accounts = self.account_manager.get_account_list()
        if not accounts:
            self.log_message("ℹ️ 没有找到任何账号", "INFO")
            return
        
        self.log_message("🔍 开始验证所有账号的cookies...")
        
        valid_count = 0
        total_count = len(accounts)
        
        for account in accounts:
            success, message = self.account_manager.validate_cookies(account)
            if success:
                self.log_message(f"✅ {account}: {message}", "SUCCESS")
                valid_count += 1
            else:
                self.log_message(f"❌ {account}: {message}", "ERROR")
        
        self.log_message(f"📊 验证完成: {valid_count}/{total_count} 个账号有效", "SUCCESS")
        self.refresh_account_list()
    
    def check_chromedriver_update(self):
        """检查ChromeDriver更新"""
        if not CHROMEDRIVER_UPDATER_AVAILABLE:
            self.log_message("❌ ChromeDriver更新模块不可用，请确保已安装requests库")
            self.chromedriver_status_label.config(text="更新模块不可用")
            return
        
        def update_callback(message):
            self.log_message(message)
            self.chromedriver_status_label.config(text=message)
            self.root.update()
        
        def check_worker():
            try:
                updater = ChromeDriverUpdater()
                update_info = updater.check_for_updates(update_callback)
                
                if update_info:
                    self.log_message(f"发现新版本: {update_info['version']}")
                    self.log_message(f"下载链接: {update_info['manual_download_url']}")
                    self.chromedriver_status_label.config(text=f"发现新版本: {update_info['version']}")
                    
                    # 显示手动下载说明
                    self.show_manual_download_dialog(update_info)
                else:
                    self.log_message("ChromeDriver已是最新版本")
                    self.chromedriver_status_label.config(text="已是最新版本")
                    
            except Exception as e:
                error_msg = f"检查更新时出错: {str(e)}"
                self.log_message(error_msg)
                self.chromedriver_status_label.config(text="检查失败")
        
        # 在新线程中运行检查
        threading.Thread(target=check_worker, daemon=True).start()

    def show_manual_download_dialog(self, update_info):
        """显示手动下载对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("ChromeDriver手动下载")
        dialog.geometry("600x500")
        dialog.resizable(True, True)
        dialog.transient(self.root)
        dialog.grab_set()
        
        # 居中显示
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f"600x500+{x}+{y}")
        
        # 创建滚动文本框
        frame = ttk.Frame(dialog)
        frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 标题
        title_label = ttk.Label(frame, text="ChromeDriver手动下载说明", font=('Arial', 12, 'bold'))
        title_label.pack(pady=(0, 10))
        
        # 创建文本框和滚动条
        text_frame = ttk.Frame(frame)
        text_frame.pack(fill='both', expand=True)
        
        text_widget = tk.Text(text_frame, wrap='word', font=('Consolas', 9))
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 插入内容
        content = f"""ChromeDriver {update_info['version']} 手动下载说明

1. 访问官方下载页面：
   https://googlechromelabs.github.io/chrome-for-testing/#stable

2. 直接下载链接：
   {update_info['manual_download_url']}

3. 下载完成后：
   - 解压zip文件
   - 将解压出的 chromedriver.exe 文件复制到当前程序目录
   - 替换现有的 chromedriver.exe 文件

4. 验证安装：
   - 运行 .\\chromedriver.exe --version 检查版本
   - 应该显示：ChromeDriver {update_info['version']}

5. 注意事项：
   - 确保下载的是 {update_info['system']} 版本
   - 下载完成后建议重启程序
   - 如果自动更新失败，可以尝试手动下载

当前检测到的平台：{update_info['system']}
最新版本：{update_info['version']}
"""
        
        text_widget.insert('1.0', content)
        text_widget.config(state='disabled')  # 设置为只读
        
        # 按钮框架
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill='x', pady=(10, 0))
        
        # 复制链接按钮
        def copy_link():
            self.root.clipboard_clear()
            self.root.clipboard_append(update_info['manual_download_url'])
            messagebox.showinfo("复制成功", "下载链接已复制到剪贴板")
        
        copy_button = ttk.Button(button_frame, text="复制下载链接", command=copy_link)
        copy_button.pack(side='left', padx=(0, 10))
        
        # 关闭按钮
        close_button = ttk.Button(button_frame, text="关闭", command=dialog.destroy)
        close_button.pack(side='right')
    
    def update_chromedriver(self):
        """更新ChromeDriver"""
        if not CHROMEDRIVER_UPDATER_AVAILABLE:
            self.log_message("❌ ChromeDriver更新模块不可用，请确保已安装requests库")
            return
        
        # 确认对话框
        result = messagebox.askyesno("确认更新", 
                                   "确定要更新ChromeDriver吗？\n\n"
                                   "更新过程中程序可能会暂时无响应，请耐心等待。\n"
                                   "更新完成后需要重启程序。")
        if not result:
            return
        
        def update_callback(message):
            self.log_message(message)
            self.chromedriver_status_label.config(text=message)
            self.root.update()
        
        def update_worker():
            try:
                updater = ChromeDriverUpdater()
                success = updater.update_chromedriver(update_callback)
                
                if success:
                    self.log_message("✅ ChromeDriver更新成功！")
                    self.chromedriver_status_label.config(text="更新成功")
                    messagebox.showinfo("更新完成", 
                                      "ChromeDriver更新成功！\n\n"
                                      "建议重启程序以确保新版本生效。")
                else:
                    self.log_message("❌ ChromeDriver更新失败")
                    self.chromedriver_status_label.config(text="更新失败")
                    
                    # 获取最新版本信息并显示手动下载对话框
                    try:
                        latest_info = updater.get_latest_chromedriver_info()
                        if latest_info:
                            messagebox.showerror("更新失败", 
                                               "ChromeDriver自动更新失败。\n\n"
                                               "将显示手动下载说明。")
                            self.show_manual_download_dialog(latest_info)
                        else:
                            messagebox.showerror("更新失败", 
                                               "ChromeDriver更新失败，请检查网络连接或手动下载。")
                    except:
                        messagebox.showerror("更新失败", 
                                           "ChromeDriver更新失败，请检查网络连接或手动下载。")
                    
            except Exception as e:
                error_msg = f"更新时出错: {str(e)}"
                self.log_message(error_msg)
                self.chromedriver_status_label.config(text="更新出错")
                messagebox.showerror("更新错误", error_msg)
        
        # 在新线程中运行更新
        threading.Thread(target=update_worker, daemon=True).start()

    def force_update_chromedriver(self):
        """强制更新ChromeDriver"""
        if not CHROMEDRIVER_UPDATER_AVAILABLE:
            self.log_message("❌ ChromeDriver更新模块不可用，请确保已安装requests库")
            return

        # 确认对话框
        result = messagebox.askyesno("确认强制更新",
                                   "确定要强制更新ChromeDriver吗？\n\n"
                                   "这将下载最新版本并替换当前版本，不管当前版本是什么。\n"
                                   "更新过程中程序可能会暂时无响应，请耐心等待。\n"
                                   "更新完成后需要重启程序。")
        if not result:
            return

        def update_callback(message):
            self.log_message(message)
            self.chromedriver_status_label.config(text=message)
            self.root.update()

        def force_update_worker():
            try:
                updater = ChromeDriverUpdater()
                success = updater.force_update_chromedriver(update_callback)

                if success:
                    self.log_message("✅ ChromeDriver强制更新成功！")
                    self.chromedriver_status_label.config(text="强制更新成功")
                    messagebox.showinfo("更新完成",
                                      "ChromeDriver强制更新成功！\n\n"
                                      "建议重启程序以确保新版本生效。")
                else:
                    self.log_message("❌ ChromeDriver强制更新失败")
                    self.chromedriver_status_label.config(text="强制更新失败")
                    
                    # 获取最新版本信息并显示手动下载对话框
                    try:
                        latest_info = updater.get_latest_chromedriver_info()
                        if latest_info:
                            messagebox.showerror("强制更新失败", 
                                               "ChromeDriver强制更新失败。\n\n"
                                               "将显示手动下载说明。")
                            self.show_manual_download_dialog(latest_info)
                        else:
                            messagebox.showerror("强制更新失败",
                                               "ChromeDriver强制更新失败，请检查网络连接或手动下载。")
                    except:
                        messagebox.showerror("强制更新失败",
                                           "ChromeDriver强制更新失败，请检查网络连接或手动下载。")

            except Exception as e:
                error_msg = f"强制更新时出错: {str(e)}"
                self.log_message(error_msg)
                self.chromedriver_status_label.config(text="强制更新出错")
                messagebox.showerror("更新错误", error_msg)

        # 在新线程中运行强制更新
        threading.Thread(target=force_update_worker, daemon=True).start()

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
    try:
        root = tk.Tk()
        app = MicrosoftRewardsGUI(root)
        
        # 设置窗口关闭事件
        def on_closing():
            if app.is_running:
                if messagebox.askokcancel("退出", "程序正在运行中，确定要退出吗？"):
                    app.is_running = False
                    # 保存窗口几何信息
                    if app.config_manager:
                        app.config_manager.save_window_geometry(root.geometry())
                    root.destroy()
            else:
                # 保存窗口几何信息
                if app.config_manager:
                    app.config_manager.save_window_geometry(root.geometry())
                root.destroy()
        
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # 启动GUI
        root.mainloop()
    except Exception as e:
        # 如果GUI启动失败，显示错误信息
        import traceback
        error_msg = f"程序启动失败: {str(e)}\n\n详细错误信息:\n{traceback.format_exc()}"
        print(error_msg)
        
        # 尝试显示错误对话框
        try:
            import tkinter.messagebox as msgbox
            msgbox.showerror("启动错误", error_msg)
        except:
            print("无法显示错误对话框")
            input("按回车键退出...")

if __name__ == "__main__":
    main() 