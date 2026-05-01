# 软件拦截卫士 (Python版) v2.0

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> 一款用Python编写的系统保护工具，专门用于拦截鲁大师、360、2345等流氓软件的自动安装和广告推送。

## 功能特性

### v2.0 核心功能

- **强制管理员提权** - 程序启动自动获取管理员权限，双击直接运行
- **安装进程秒杀** - 检测到安装程序立即杀死，阻止安装
- **白名单保护** - 不误杀360急救箱、Steam、GitHub、火绒、UU加速器等正常软件
- **进程监控拦截** - 实时监控并终止可疑安装程序
- **Hosts文件拦截** - 自动修改Hosts文件阻断广告域名
- **注册表保护** - 阻止流氓软件添加开机启动项
- **文件监控** - 自动识别并删除可疑安装包
- **系统托盘** - 最小化到托盘，后台持续保护

### 附加功能
- **Hosts自动备份** - 每次修改前自动备份原hosts
- **一键还原** - 可恢复到任意历史备份版本
- **域名白名单** - 避免误拦截正常网站
- **智能规则校验** - 避免重复写入hosts，防止hosts文件被写爆

## 环境要求

- **Windows 7/10/11**
- **Python 3.8 或更高版本**
- 已自动获取管理员权限，无需手动操作

### 安装Python

如果还没有安装Python：
1. 访问 https://www.python.org/downloads/
2. 下载 Python 3.8+ 版本
3. 安装时勾选 **"Add Python to PATH"**

## 快速开始

### 方法一：直接双击运行（推荐）

1. 下载本项目所有文件
2. 解压到任意文件夹（如 `D:\SoftwareBlocker`）
3. **双击运行 `main.py`**
4. 程序自动获取管理员权限并启动

### 方法二：使用批处理启动

```bash
双击运行 run_as_admin.bat
```

### 方法三：静默启动（无窗口）

双击运行 `silent_start.vbs`，程序在后台静默运行

## 文件说明

```
SoftwareBlocker/
├── main.py                 # 主程序源码（自动管理员提权）
├── requirements.txt        # Python依赖包列表
├── run_as_admin.bat       # 管理员权限启动脚本
├── silent_start.vbs       # 静默启动脚本
├── config/
│   └── config.json        # 拦截规则配置文件（自动生成）
│   └── block_log.txt      # 拦截日志（自动生成）
├── backup/                # Hosts备份目录（自动生成）
└── README.md              # 本文件
```

## 安装进程秒杀功能

程序会自动检测并杀死以下关键词的安装程序：

```
360setup, 2345setup, LDSsetup, ludashi, 鲁大师, 
haozip, duba, jinshan, pcmgr, qqpcmgr
```

一旦检测到包含这些关键词的进程，**立即强制杀死**，阻止安装！

## 白名单保护

以下软件受到保护，**不会被拦截、不会被删除**：

### 360急救箱系列
- 360急救箱.exe
- 360SysRepair.exe
- 360EmergencyBox.exe
- 360Rs.exe
- 360Repair.exe
- 360SysAssist.exe

### 正常软件
- Steam (steam.exe, steamwebhelper.exe)
- GitHub (github.exe, git.exe)
- 火绒安全 (huorong.exe, hips.exe, hrkill.exe)
- UU加速器 (uu.exe, uuaccelerator.exe)

## 使用方法

### 主界面

启动后会显示主窗口，包含：
- **状态栏**：显示程序运行状态（管理员权限）
- **拦截记录列表**：实时显示拦截操作
- **操作按钮**：
  - 手动检查 - 立即执行全面检查
  - 更新Hosts - 更新广告域名拦截规则
  - Hosts管理 - 备份/还原Hosts文件
  - 白名单 - 管理免拦截项目
  - 编辑规则 - 自定义拦截规则
  - 查看日志 - 查看历史拦截记录

### 系统托盘

点击【最小化到托盘】按钮：
- 程序隐藏到系统托盘
- 左键单击托盘图标显示主窗口
- 右键菜单可快速操作

## 测试拦截功能

### 测试1：安装进程秒杀

1. 复制任意exe文件
2. 重命名为 `360setup.exe` 或 `ludashi.exe`
3. 双击运行
4. **预期结果**：程序立即被杀死，显示"安装秒杀"

### 测试2：进程拦截

1. 复制任意exe文件
2. 重命名为 `360se.exe`
3. 双击运行
4. **预期结果**：主窗口显示"终止进程：360se.exe"

### 测试3：Hosts拦截

1. 点击主界面【更新Hosts】
2. 打开浏览器访问 `2345.com`
3. **预期结果**：无法访问（被Hosts拦截）

### 测试4：白名单保护

1. 复制任意exe文件
2. 重命名为 `steam.exe`
3. 双击运行
4. **预期结果**：程序正常运行，不被拦截

## 支持的拦截目标

### 已内置支持

- **鲁大师系列** - 鲁大师主程序、游戏助手等
- **360系列** - 360安全卫士、360浏览器、360杀毒等
- **2345系列** - 2345浏览器、2345看图王、2345好压等
- **金山系列** - 毒霸、金山卫士等
- **QQ电脑管家** - qqpcmgr等

### 内置广告域名

包含60+广告服务器域名

## 配置文件说明

配置文件位于 `config\config.json`：

```json
{
  "software_list": {
    "block_processes": ["进程名.exe"],
    "install_killers": ["安装程序关键词"]
  },
  "whitelist": {
    "processes": ["白名单进程.exe"],
    "domains": ["白名单域名.com"]
  },
  "ad_servers": ["0.0.0.0 域名.com"],
  "settings": {
    "check_interval": 2
  }
}
```

## 常见问题

### Q1: 提示"未检测到Python环境"

**A**: 
1. 访问 https://www.python.org/downloads/ 下载Python
2. 安装时务必勾选 **"Add Python to PATH"**
3. 安装完成后重新运行

### Q2: 程序无法获取管理员权限

**A**:
1. 确保系统UAC没有关闭
2. 右键点击程序，选择"以管理员身份运行"
3. 检查杀毒软件是否阻止提权

### Q3: Hosts更新失败

**A**:
1. 确保程序已获取管理员权限
2. 检查杀毒软件是否保护Hosts文件

### Q4: 误拦截了正常软件

**A**:
1. 点击【白名单】按钮
2. 将误拦截的软件添加到白名单
3. 保存后重启程序

### Q5: 如何彻底卸载拦截的软件

**A**:
1. 先运行本程序阻止其自保护
2. 使用系统自带的卸载程序卸载
3. 运行CCleaner等工具清理残留

## 技术原理

### 强制管理员提权
```python
ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, ...)
```

### 安装进程秒杀
- 检测进程名是否包含安装关键词
- 发现后立即调用 `kill()` 强制终止
- 同时删除安装文件

### 白名单保护
- 进程启动前检查白名单
- 白名单中的进程直接放行
- 不误杀正常软件

## 依赖包

| 包名 | 版本 | 用途 |
|------|------|------|
| psutil | >=5.9.0 | 进程监控 |
| watchdog | >=3.0.0 | 文件监控 |
| pystray | >=0.19.0 | 系统托盘 |
| pillow | >=9.0.0 | 托盘图标 |

## 更新日志

### v2.0 (2026-4-27)
- 新增强制管理员提权功能
- 新增安装进程秒杀功能
- 新增白名单保护机制
- 保护360急救箱、Steam、GitHub、火绒、UU加速器
- 保留全部原有功能

### v1.1 (2026-4-25)
- 新增Hosts自动备份与一键还原
- 新增域名白名单机制
- 新增智能规则校验

### v1.0 (2026-3-12)
- 初始版本发布

## 许可证

本项目采用 [CC BY-NC-SA 4.0](LICENSE) 许可证开源。

## 免责声明

本软件仅供学习研究使用，请勿用于非法用途。使用本软件造成的任何后果由用户自行承担。

---
© 2024 Alaswint. All rights reserved.
本项目采用 CC BY-NC-SA 4.0 协议开源，严格禁止任何形式的商用、售卖、盈利

**如果觉得本项目对你有帮助，请给个 Star
