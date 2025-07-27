# Microsoft Rewards 自动化工具

这是一个用于自动化Microsoft Rewards搜索的工具，包含获取cookies和自动搜索功能。

## 功能特点

- 🔐 **自动检测登录状态**: 程序会自动检测登录按钮的变化，无需手动计时
- 🍪 **智能保存Cookies**: 登录成功后自动保存cookies到文件
- 🔍 **自动搜索**: 支持桌面端和移动端自动搜索
- 📊 **详细日志**: 提供清晰的状态反馈和进度显示
- 🛡️ **错误处理**: 完善的异常处理和用户友好的错误提示

## 📁 文件说明

### 🔧 核心工具
- `get_cookie.py`: 智能登录检测工具（获取cookies）
- `search.py`: 完整自动搜索工具（桌面端+移动端）
- `desktop_search.py`: 桌面端专用搜索工具
- `mobile_search.py`: 移动端专用搜索工具

### 🚀 启动脚本
- `search.bat`: Windows批处理文件，启动完整搜索
- `desktop_search.bat`: Windows批处理文件，启动桌面端搜索
- `mobile_search.bat`: Windows批处理文件，启动移动端搜索

### 🛠️ 辅助工具
- `validate_cookies.py`: Cookies验证工具（诊断cookies问题）
- `custom_search_terms.py`: 自定义搜索词配置文件
- `chromedriver.exe`: Chrome浏览器驱动
- `requirements.txt`: Python依赖管理文件

## 使用方法

### 1. 获取Cookies

运行智能登录检测工具：

```bash
python get_cookie.py
```

程序会：
1. 自动打开Chrome浏览器
2. 访问必应首页
3. 等待你手动登录Microsoft账户
4. 智能检测登录状态变化（包括页面跳转）
5. 登录成功后自动保存cookies到`cookies.txt`文件

**注意**: 
- 程序会每5秒检查一次登录状态，最多等待5分钟
- 能够处理登录页面跳转的情况
- 检测多种登录成功的标志

### 2. 自动搜索

获取cookies后，可以选择以下方式执行搜索：

#### 方式一：完整搜索（桌面端+移动端）
```bash
python search.py
```
或者使用批处理文件：
```bash
search.bat
```

#### 方式二：分别搜索

**桌面端搜索（30次）：**
```bash
python desktop_search.py
```
或者：
```bash
desktop_search.bat
```

**移动端搜索（20次）：**
```bash
python mobile_search.py
```
或者：
```bash
mobile_search.bat
```

### 3. 验证Cookies（可选）

如果遇到cookies问题，可以运行验证工具：

```bash
python validate_cookies.py
```

### 4. 自定义搜索词（可选）

你可以编辑 `custom_search_terms.py` 文件来自定义搜索词：

```bash
# 编辑自定义搜索词文件
notepad custom_search_terms.py
```

程序会优先使用自定义搜索词，如果没有自定义文件则使用默认搜索词。





搜索工具会：
1. 使用保存的cookies自动登录
2. 执行桌面端搜索（30次，间隔8秒）- 模拟真实用户输入，使用随机搜索词
3. 执行移动端搜索（20次，间隔8秒）- 模拟真实用户输入，使用随机搜索词
4. 自动完成每日搜索任务

## 系统要求

- Python 3.6+
- Chrome浏览器
- ChromeDriver（放在当前目录下）

## 依赖安装

```bash
pip install -r requirements.txt
```

或者手动安装：

```bash
pip install selenium
```

## 注意事项

1. **首次使用**: 必须先运行`get_cookie.py`获取cookies
2. **登录状态**: 确保在程序运行期间完成Microsoft账户登录
3. **网络连接**: 确保网络连接稳定
4. **ChromeDriver**: 确保当前目录下有chromedriver.exe文件

## 故障排除

### 常见问题

1. **ChromeDriver错误**
   - 确保ChromeDriver版本与Chrome浏览器版本匹配
   - 下载对应版本的ChromeDriver

2. **ChromeDriver版本不兼容**
   - 下载最新版本的ChromeDriver
   - 将chromedriver.exe放在当前目录下

3. **登录检测失败**
   - 检查网络连接
   - 确保在必应首页进行登录
   - 尝试刷新页面后重新登录

4. **Cookies加载失败**
   - 运行 `python validate_cookies.py` 诊断cookies问题
   - 检查cookies是否过期
   - 重新运行`get_cookie.py`获取新的cookies

5. **搜索失败**
   - 检查网络连接
   - 确保cookies有效

### 日志说明

程序会显示详细的执行日志：
- ✅ 成功操作
- ❌ 错误操作
- ⚠️ 警告信息
- 📊 统计信息

## 免责声明

本工具仅供学习和研究使用，请遵守Microsoft Rewards的使用条款。使用者需自行承担使用风险。

## 更新日志

### v2.0
- 添加自动登录状态检测
- 优化用户界面和日志输出
- 增强错误处理机制
- 添加详细的进度显示


![meteor-comet's GitHub stats](https://github-readme-stats.vercel.app/api?username=meteor-comet&show_icons=true&theme=radical)