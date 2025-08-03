#!/usr/bin/env python3
"""
配置管理模块
用于保存和加载程序设置
"""

import json
import os

class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.default_config = {
            "search_settings": {
                "interval": "8",
                "desktop_count": "30",
                "mobile_count": "20",
                "search_type": "both"
            },
            "last_account": "",
            "window_geometry": "",
            "auto_save_cookies": True
        }
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置，确保所有必要的键都存在
                    return self.merge_configs(self.default_config, config)
            else:
                return self.default_config.copy()
        except Exception as e:
            print(f"加载配置文件时出错: {e}")
            return self.default_config.copy()
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置文件时出错: {e}")
            return False
    
    def merge_configs(self, default, user):
        """合并默认配置和用户配置"""
        result = default.copy()
        for key, value in user.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.merge_configs(result[key], value)
            else:
                result[key] = value
        return result
    
    def get_search_settings(self):
        """获取搜索设置"""
        return self.config.get("search_settings", self.default_config["search_settings"])
    
    def save_search_settings(self, interval, desktop_count, mobile_count, search_type):
        """保存搜索设置"""
        self.config["search_settings"] = {
            "interval": str(interval),
            "desktop_count": str(desktop_count),
            "mobile_count": str(mobile_count),
            "search_type": search_type
        }
        return self.save_config()
    
    def get_last_account(self):
        """获取上次使用的账号"""
        return self.config.get("last_account", "")
    
    def save_last_account(self, account_name):
        """保存上次使用的账号"""
        self.config["last_account"] = account_name
        return self.save_config()
    
    def get_window_geometry(self):
        """获取窗口几何信息"""
        return self.config.get("window_geometry", "")
    
    def save_window_geometry(self, geometry):
        """保存窗口几何信息"""
        self.config["window_geometry"] = geometry
        return self.save_config()
    
    def get_auto_save_cookies(self):
        """获取自动保存cookies设置"""
        return self.config.get("auto_save_cookies", True)
    
    def save_auto_save_cookies(self, auto_save):
        """保存自动保存cookies设置"""
        self.config["auto_save_cookies"] = auto_save
        return self.save_config() 