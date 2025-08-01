#!/usr/bin/env python3
"""
测试GUI配置功能
"""

import tkinter as tk
from tkinter import ttk
from config_manager import ConfigManager

def test_gui_config():
    """测试GUI配置功能"""
    print("=== GUI配置测试 ===")
    
    # 创建测试窗口
    root = tk.Tk()
    root.title("配置测试")
    root.geometry("400x300")
    
    # 创建配置管理器
    config = ConfigManager("test_gui_config.json")
    
    # 创建测试变量
    interval_var = tk.StringVar(value="8")
    desktop_count_var = tk.StringVar(value="30")
    mobile_count_var = tk.StringVar(value="20")
    search_type = tk.StringVar(value="both")
    
    # 创建界面
    frame = ttk.Frame(root, padding=10)
    frame.pack(fill='both', expand=True)
    
    # 搜索参数
    ttk.Label(frame, text="搜索参数测试", font=('Arial', 12, 'bold')).pack(pady=5)
    
    # 间隔
    interval_frame = ttk.Frame(frame)
    interval_frame.pack(fill='x', pady=2)
    ttk.Label(interval_frame, text="搜索间隔:").pack(side='left')
    ttk.Entry(interval_frame, textvariable=interval_var, width=10).pack(side='left', padx=5)
    
    # 桌面端次数
    desktop_frame = ttk.Frame(frame)
    desktop_frame.pack(fill='x', pady=2)
    ttk.Label(desktop_frame, text="桌面端次数:").pack(side='left')
    ttk.Entry(desktop_frame, textvariable=desktop_count_var, width=10).pack(side='left', padx=5)
    
    # 移动端次数
    mobile_frame = ttk.Frame(frame)
    mobile_frame.pack(fill='x', pady=2)
    ttk.Label(mobile_frame, text="移动端次数:").pack(side='left')
    ttk.Entry(mobile_frame, textvariable=mobile_count_var, width=10).pack(side='left', padx=5)
    
    # 搜索类型
    type_frame = ttk.Frame(frame)
    type_frame.pack(fill='x', pady=2)
    ttk.Label(type_frame, text="搜索类型:").pack(side='left')
    ttk.Radiobutton(type_frame, text="桌面端", variable=search_type, value="desktop").pack(side='left')
    ttk.Radiobutton(type_frame, text="移动端", variable=search_type, value="mobile").pack(side='left')
    ttk.Radiobutton(type_frame, text="完整搜索", variable=search_type, value="both").pack(side='left')
    
    # 按钮
    button_frame = ttk.Frame(frame)
    button_frame.pack(fill='x', pady=10)
    
    def save_settings():
        """保存设置"""
        success = config.save_search_settings(
            interval_var.get(),
            desktop_count_var.get(),
            mobile_count_var.get(),
            search_type.get()
        )
        if success:
            print("✅ 设置保存成功")
            result_label.config(text="✅ 设置已保存", foreground="green")
        else:
            print("❌ 设置保存失败")
            result_label.config(text="❌ 保存失败", foreground="red")
    
    def load_settings():
        """加载设置"""
        settings = config.get_search_settings()
        interval_var.set(settings.get('interval', '8'))
        desktop_count_var.set(settings.get('desktop_count', '30'))
        mobile_count_var.set(settings.get('mobile_count', '20'))
        search_type.set(settings.get('search_type', 'both'))
        print("✅ 设置加载成功")
        result_label.config(text="✅ 设置已加载", foreground="green")
    
    ttk.Button(button_frame, text="💾 保存设置", command=save_settings).pack(side='left', padx=5)
    ttk.Button(button_frame, text="📂 加载设置", command=load_settings).pack(side='left', padx=5)
    
    # 结果显示
    result_label = ttk.Label(frame, text="等待操作...")
    result_label.pack(pady=10)
    
    # 显示当前配置
    info_frame = ttk.LabelFrame(frame, text="当前配置", padding=5)
    info_frame.pack(fill='x', pady=5)
    
    info_text = f"""
间隔: {interval_var.get()} 秒
桌面端: {desktop_count_var.get()} 次
移动端: {mobile_count_var.get()} 次
搜索类型: {search_type.get()}
    """
    
    info_label = ttk.Label(info_frame, text=info_text, justify='left')
    info_label.pack()
    
    # 启动GUI
    print("GUI测试窗口已打开，请测试保存和加载功能")
    root.mainloop()

if __name__ == "__main__":
    test_gui_config() 