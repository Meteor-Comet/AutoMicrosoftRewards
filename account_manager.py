#!/usr/bin/env python3
"""
账号管理模块
"""

import json
import os
import shutil
from datetime import datetime

class AccountManager:
    def __init__(self, accounts_dir="accounts"):
        self.accounts_dir = accounts_dir
        self.accounts_file = "accounts.json"
        self.current_account = None
        self.ensure_accounts_dir()
        self.load_accounts()
    
    def ensure_accounts_dir(self):
        """确保账号目录存在"""
        if not os.path.exists(self.accounts_dir):
            os.makedirs(self.accounts_dir)
    
    def load_accounts(self):
        """加载账号列表"""
        try:
            if os.path.exists(self.accounts_file):
                with open(self.accounts_file, 'r', encoding='utf-8') as f:
                    self.accounts = json.load(f)
            else:
                self.accounts = {}
        except Exception:
            self.accounts = {}
    
    def save_accounts(self):
        """保存账号列表"""
        try:
            with open(self.accounts_file, 'w', encoding='utf-8') as f:
                json.dump(self.accounts, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False
    
    def add_account(self, account_name, email=None, description=None):
        """添加新账号"""
        if account_name in self.accounts:
            return False, "账号名称已存在"
        
        account_info = {
            "email": email or "",
            "description": description or "",
            "created_time": datetime.now().isoformat(),
            "last_login": None,
            "cookies_file": f"cookies_{account_name}.txt"
        }
        
        self.accounts[account_name] = account_info
        if self.save_accounts():
            return True, f"账号 '{account_name}' 添加成功"
        else:
            return False, "保存账号信息失败"
    
    def remove_account(self, account_name):
        """删除账号"""
        if account_name not in self.accounts:
            return False, "账号不存在"
        
        # 删除cookies文件
        cookies_file = self.accounts[account_name]["cookies_file"]
        if os.path.exists(cookies_file):
            try:
                os.remove(cookies_file)
            except Exception:
                pass
        
        # 从账号列表中删除
        del self.accounts[account_name]
        
        if self.save_accounts():
            return True, f"账号 '{account_name}' 删除成功"
        else:
            return False, "删除账号失败"
    
    def switch_account(self, account_name):
        """切换账号"""
        if account_name not in self.accounts:
            return False, "账号不存在"
        
        # 备份当前cookies（如果存在）
        if os.path.exists("cookies.txt"):
            current_account = self.get_current_account_name()
            if current_account:
                backup_file = f"cookies_{current_account}.txt"
                try:
                    shutil.copy("cookies.txt", backup_file)
                except Exception:
                    pass
        
        # 切换到新账号的cookies
        target_cookies = self.accounts[account_name]["cookies_file"]
        
        if os.path.exists(target_cookies):
            try:
                shutil.copy(target_cookies, "cookies.txt")
            except Exception:
                return False, "复制cookies文件失败"
        else:
            # 如果目标账号没有cookies文件，删除当前的
            if os.path.exists("cookies.txt"):
                try:
                    os.remove("cookies.txt")
                except Exception:
                    pass
        
        self.current_account = account_name
        
        # 更新最后登录时间
        self.accounts[account_name]["last_login"] = datetime.now().isoformat()
        self.save_accounts()
        
        return True, f"已切换到账号 '{account_name}'"
    
    def switch_to_account(self, account_name):
        """切换到指定账号（简化版本，用于全部账号任务）"""
        if account_name not in self.accounts:
            raise ValueError(f"账号 '{account_name}' 不存在")
        
        # 备份当前cookies（如果存在）
        if os.path.exists("cookies.txt"):
            current_account = self.get_current_account_name()
            if current_account:
                backup_file = f"cookies_{current_account}.txt"
                try:
                    shutil.copy("cookies.txt", backup_file)
                except Exception:
                    pass
        
        # 切换到新账号的cookies
        target_cookies = self.accounts[account_name]["cookies_file"]
        
        if os.path.exists(target_cookies):
            try:
                shutil.copy(target_cookies, "cookies.txt")
                self.current_account = account_name
                return True
            except Exception as e:
                raise Exception(f"切换账号失败: {e}")
        else:
            raise Exception(f"账号 '{account_name}' 的cookies文件不存在")
    
    def save_current_cookies(self, account_name=None):
        """保存当前cookies到指定账号"""
        if not account_name:
            account_name = self.current_account
        
        if not account_name or account_name not in self.accounts:
            return False, "无效的账号名称"
        
        if not os.path.exists("cookies.txt"):
            return False, "当前没有cookies文件"
        
        target_file = self.accounts[account_name]["cookies_file"]
        try:
            shutil.copy("cookies.txt", target_file)
            self.accounts[account_name]["last_login"] = datetime.now().isoformat()
            self.save_accounts()
            return True, f"cookies已保存到账号 '{account_name}'"
        except Exception as e:
            return False, f"保存cookies失败: {str(e)}"
    
    def get_account_list(self):
        """获取账号列表"""
        return list(self.accounts.keys())
    
    def get_all_accounts(self):
        """获取所有账号名称列表"""
        return list(self.accounts.keys())
    
    def get_account_info(self, account_name):
        """获取账号信息"""
        if account_name in self.accounts:
            return self.accounts[account_name]
        return None
    
    def get_current_account_name(self):
        """获取当前账号名称"""
        if not self.current_account:
            # 尝试从cookies文件推断当前账号
            if os.path.exists("cookies.txt"):
                for account_name, info in self.accounts.items():
                    if info["cookies_file"] == "cookies.txt":
                        self.current_account = account_name
                        break
        return self.current_account
    
    def has_cookies(self, account_name):
        """检查账号是否有cookies"""
        if account_name not in self.accounts:
            return False
        cookies_file = self.accounts[account_name]["cookies_file"]
        return os.path.exists(cookies_file)
    
    def validate_cookies(self, account_name):
        """验证账号cookies"""
        if account_name not in self.accounts:
            return False, "账号不存在"
        
        cookies_file = self.accounts[account_name]["cookies_file"]
        if not os.path.exists(cookies_file):
            return False, "cookies文件不存在"
        
        try:
            with open(cookies_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            
            valid_count = 0
            total_count = len(cookies)
            
            for cookie in cookies:
                if cookie.get('name') and cookie.get('value'):
                    valid_count += 1
            
            return True, f"{valid_count}/{total_count} 个cookies有效"
        except Exception as e:
            return False, f"验证cookies失败: {str(e)}"
    
    def get_account_status(self, account_name):
        """获取账号状态"""
        if account_name not in self.accounts:
            return "不存在"
        
        info = self.accounts[account_name]
        has_cookies = self.has_cookies(account_name)
        
        if has_cookies:
            return "已登录"
        else:
            return "未登录" 