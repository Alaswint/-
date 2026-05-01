#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
软件拦截卫士 - Python版本 v2.1
功能：拦截鲁大师、360、2345等流氓软件的自动安装和广告推送
新增：强制管理员提权、安装进程秒杀、白名单保护、黑名单管理、完善自启功能
作者：AI Assistant
版本：2.1
"""

import os
import sys
import json
import time
import threading
import subprocess
import re
import shutil
import glob
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

# ============ 强制管理员提权 ============
def is_admin():
    """检查是否以管理员身份运行"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """以管理员权限重新运行程序"""
    if not is_admin():
        try:
            import ctypes
            # 使用ShellExecute以管理员权限重新运行
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit(0)
        except Exception as e:
            print(f"提权失败: {e}")
            messagebox.showerror("错误", "需要管理员权限才能运行此程序！\n请右键选择'以管理员身份运行'")
            sys.exit(1)

# 启动时立即提权
run_as_admin()

# ============ 检查并安装依赖 ============
def check_and_install_dependencies():
    """检查并安装必要的依赖包"""
    required = {
        'psutil': 'psutil',
        'watchdog': 'watchdog',
        'pystray': 'pystray',
        'pillow': 'PIL'
    }
    
    missing = []
    for package, import_name in required.items():
        try:
            __import__(import_name)
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"正在安装依赖包: {', '.join(missing)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing)
            print("依赖包安装完成")
        except Exception as e:
            print(f"安装依赖失败: {e}")
            messagebox.showerror("错误", f"安装依赖失败: {e}\n请手动运行: pip install {' '.join(missing)}")
            sys.exit(1)

check_and_install_dependencies()

import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pystray
from PIL import Image, ImageDraw

# ============ 全局配置 ============
APP_NAME = "软件拦截卫士"
APP_VERSION = "2.1"
CONFIG_DIR = Path(__file__).parent / "config"
CONFIG_FILE = CONFIG_DIR / "config.json"
LOG_FILE = CONFIG_DIR / "block_log.txt"
BACKUP_DIR = Path(__file__).parent / "backup"
HOSTS_FILE = Path(r"C:\Windows\System32\drivers\etc\hosts")
MAX_HOSTS_SIZE = 1024 * 1024  # 1MB
STARTUP_REG_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
STARTUP_REG_NAME = "SoftwareBlocker"

# 确保目录存在
CONFIG_DIR.mkdir(exist_ok=True)
BACKUP_DIR.mkdir(exist_ok=True)

# ============ 配置管理器 ============
class ConfigManager:
    """配置管理器"""
    
    DEFAULT_CONFIG = {
        "software_list": {
            "block_processes": [
                "鲁大师.exe", "LDS.exe", "LDSGui.exe", "LDSGameMaster.exe",
                "360installer.exe", "360se.exe", "360chrome.exe", "360Safe.exe",
                "360SafeTray.exe", "360rp.exe", "360rps.exe", "360sd.exe",
                "360netman.exe", "360leakfixer.exe",
                "2345Explorer.exe", "2345PicEditor.exe", "2345好压.exe",
                "2345加速浏览器.exe", "2345看图王.exe", "2345安全卫士.exe",
                "2345软件管家.exe", "2345王牌输入法.exe", "2345PicViewer.exe",
                "2345ExplorerFrame.exe", "2345MiniPage.exe", "2345Pic.exe",
                "HaoZip.exe", "HaoZipC.exe", "HaoZipEdit.exe",
                "duba.exe", "ksafe.exe", "kismain.exe", "kwatch.exe",
                "qqpcmgr.exe", "qqpcrtp.exe", "qqpctray.exe"
            ],
            "install_killers": [
                "360setup", "2345setup", "LDSsetup", "ludashi",
                "鲁大师", "haozip", "duba", "jinshan", 
                "pcmgr", "qqpcmgr", "ksafe", "kismain"
            ]
        },
        "whitelist": {
            "processes": [
                "360急救箱.exe", "360SysRepair.exe", "360EmergencyBox.exe",
                "360Rs.exe", "360Repair.exe", "360SysAssist.exe",
                "steam.exe", "steamwebhelper.exe",
                "github.exe", "git.exe",
                "huorong.exe", "hips.exe", "hrkill.exe",
                "uu.exe", "uuaccelerator.exe"
            ],
            "domains": [
                "localhost",
                "127.0.0.1",
                "steampowered.com",
                "steamcommunity.com",
                "github.com",
                "githubusercontent.com",
                "huorong.cn"
            ]
        },
        "blacklist": {
            "processes": [],
            "domains": []
        },
        "ad_servers": [
            "0.0.0.0 shouji.360.cn",
            "0.0.0.0 openbox.mobilem.360.cn",
            "0.0.0.0 s.360.cn",
            "0.0.0.0 s.so.360.cn",
            "0.0.0.0 haosou.com",
            "0.0.0.0 www.haosou.com",
            "0.0.0.0 so.com",
            "0.0.0.0 www.so.com",
            "0.0.0.0 2345.com",
            "0.0.0.0 www.2345.com",
            "0.0.0.0 dl.2345.com",
            "0.0.0.0 download.2345.com",
            "0.0.0.0 union.2345.com",
            "0.0.0.0 ad.2345.com",
            "0.0.0.0 soft.2345.com",
            "0.0.0.0 tongji.2345.com",
            "0.0.0.0 pic.2345.com",
            "0.0.0.0 minipage.2345.com",
            "0.0.0.0 news.2345.com",
            "0.0.0.0 game.2345.com",
            "0.0.0.0 mall.2345.com",
            "0.0.0.0 api.2345.com",
            "0.0.0.0 update.2345.com",
            "0.0.0.0 360.cn",
            "0.0.0.0 www.360.cn",
            "0.0.0.0 360safe.com",
            "0.0.0.0 www.360safe.com",
            "0.0.0.0 360totalsecurity.com",
            "0.0.0.0 www.360totalsecurity.com",
            "0.0.0.0 yunpan.360.cn",
            "0.0.0.0 yun.360.cn",
            "0.0.0.0 app.360.cn",
            "0.0.0.0 open.360.cn",
            "0.0.0.0 soft.360.cn",
            "0.0.0.0 sd.360.cn",
            "0.0.0.0 se.360.cn",
            "0.0.0.0 browser.360.cn",
            "0.0.0.0 yunpan.cn",
            "0.0.0.0 www.yunpan.cn",
            "0.0.0.0 ludashi.com",
            "0.0.0.0 www.ludashi.com",
            "0.0.0.0 lds.360.cn",
            "0.0.0.0 g.360.cn",
            "0.0.0.0 cm.360.cn",
            "0.0.0.0 p.360.cn",
            "0.0.0.0 ad.360.cn",
            "0.0.0.0 stat.360.cn",
            "0.0.0.0 log.360.cn",
            "0.0.0.0 trace.360.cn",
            "0.0.0.0 tracker.360.cn",
            "0.0.0.0 duba.net",
            "0.0.0.0 www.duba.net",
            "0.0.0.0 ijinshan.com",
            "0.0.0.0 www.ijinshan.com"
        ],
        "auto_run": {
            "block_keys": ["360", "2345", "LDS", "鲁大师", "好压", "看图王", 
                          "2345Pic", "2345Explorer", "2345Safe", "360Safe", 
                          "360se", "360chrome", "360installer", "LDSGui", 
                          "LDSGameMaster", "360netman", "360rp", "360rps", 
                          "360sd", "360leakfixer", "360Tray", "360SafeTray", 
                          "HaoZip", "duba", "jinshan", "ksafe", "qqpcmgr"]
        },
        "file_monitor": {
            "monitor_paths": [
                "${USERPROFILE}\\Downloads",
                "C:\\Windows\\Temp",
                "${TEMP}",
                "${LOCALAPPDATA}",
                "${APPDATA}",
                "C:\\ProgramData"
            ],
            "block_file_keywords": [
                "360setup", "2345setup", "LDSsetup", "鲁大师安装", 
                "好压安装", "看图王安装", "360安装", "2345安装",
                "360safe_setup", "360se_setup", "360chrome_setup",
                "2345Explorer_setup", "2345Pic_setup", "2345HaoZip_setup",
                "LDS_setup", "ludashi_setup", "duba_setup", "jinshan_setup",
                "qqpcmgr_setup", "ksafe_setup"
            ]
        },
        "settings": {
            "check_interval": 2,
            "auto_block_hosts": True,
            "monitor_process": True,
            "monitor_registry": True,
            "monitor_files": True,
            "auto_delete_files": True,
            "show_tray_tips": True,
            "max_hosts_backups": 10,
            "hosts_backup_before_update": True
        }
    }
    
    def __init__(self):
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    merged = self._merge_config(self.DEFAULT_CONFIG.copy(), loaded_config)
                    return merged
            except Exception as e:
                print(f"加载配置文件失败: {e}，使用默认配置")
        
        self.save_config(self.DEFAULT_CONFIG)
        return self.DEFAULT_CONFIG.copy()
    
    def _merge_config(self, default, loaded):
        """递归合并配置"""
        for key, value in default.items():
            if key not in loaded:
                loaded[key] = value
            elif isinstance(value, dict) and isinstance(loaded[key], dict):
                loaded[key] = self._merge_config(value, loaded[key])
        return loaded
    
    def save_config(self, config=None):
        """保存配置文件"""
        if config is None:
            config = self.config
        try:
            CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置文件失败: {e}")
    
    def get(self, key, default=None):
        """获取配置项"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value
    
    def set(self, key, value):
        """设置配置项"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save_config()


# ============ 日志管理器 ============
class Logger:
    """日志管理器"""
    
    def __init__(self):
        self.lock = threading.Lock()
    
    def log(self, block_type, detail):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{block_type}] {detail}\n"
        
        with self.lock:
            try:
                with open(LOG_FILE, 'a', encoding='utf-8') as f:
                    f.write(log_line)
            except Exception as e:
                print(f"写入日志失败: {e}")
        
        return timestamp, block_type, detail


# ============ Hosts备份管理器 ============
class HostsBackupManager:
    """Hosts备份管理器"""
    
    BACKUP_PATTERN = "hosts_backup_*.txt"
    
    def __init__(self, logger, callback=None):
        self.logger = logger
        self.callback = callback
    
    def create_backup(self):
        """创建Hosts备份"""
        try:
            if not HOSTS_FILE.exists():
                self._log("Hosts备份", "Hosts文件不存在，跳过备份")
                return None
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"hosts_backup_{timestamp}.txt"
            backup_path = BACKUP_DIR / backup_name
            
            shutil.copy2(HOSTS_FILE, backup_path)
            self._log("Hosts备份", f"成功创建备份: {backup_name}")
            
            self._cleanup_old_backups()
            return str(backup_path)
            
        except Exception as e:
            self._log("Hosts备份", f"备份失败: {str(e)}")
            return None
    
    def restore_backup(self, backup_path):
        """还原Hosts备份"""
        try:
            if not os.path.exists(backup_path):
                self._log("Hosts还原", "备份文件不存在")
                return False
            
            self.create_backup()
            shutil.copy2(backup_path, HOSTS_FILE)
            
            backup_name = os.path.basename(backup_path)
            self._log("Hosts还原", f"成功还原备份: {backup_name}")
            return True
            
        except PermissionError:
            self._log("Hosts还原", "还原失败: 需要管理员权限")
            return False
        except Exception as e:
            self._log("Hosts还原", f"还原失败: {str(e)}")
            return False
    
    def get_backup_list(self):
        """获取所有备份列表"""
        try:
            backup_pattern = str(BACKUP_DIR / self.BACKUP_PATTERN)
            backups = glob.glob(backup_pattern)
            backups.sort(key=os.path.getmtime, reverse=True)
            
            result = []
            for backup in backups:
                filename = os.path.basename(backup)
                mtime = datetime.fromtimestamp(os.path.getmtime(backup))
                size = os.path.getsize(backup)
                
                match = re.search(r'hosts_backup_(\d{8}_\d{6})\.txt', filename)
                if match:
                    time_str = match.group(1)
                    display_time = f"{time_str[:4]}-{time_str[4:6]}-{time_str[6:8]} {time_str[9:11]}:{time_str[11:13]}:{time_str[13:15]}"
                else:
                    display_time = mtime.strftime("%Y-%m-%d %H:%M:%S")
                
                result.append({
                    'path': backup,
                    'filename': filename,
                    'time': display_time,
                    'size': f"{size / 1024:.1f} KB"
                })
            
            return result
            
        except Exception as e:
            print(f"获取备份列表失败: {e}")
            return []
    
    def delete_backup(self, backup_path):
        """删除指定备份"""
        try:
            if os.path.exists(backup_path):
                os.remove(backup_path)
                self._log("Hosts备份", f"已删除备份: {os.path.basename(backup_path)}")
                return True
            return False
        except Exception as e:
            self._log("Hosts备份", f"删除备份失败: {str(e)}")
            return False
    
    def _cleanup_old_backups(self):
        """清理旧备份"""
        try:
            backups = self.get_backup_list()
            max_backups = 10
            
            if len(backups) > max_backups:
                for backup in backups[max_backups:]:
                    os.remove(backup['path'])
                    
        except Exception as e:
            print(f"清理旧备份失败: {e}")
    
    def _log(self, block_type, detail):
        """记录日志"""
        result = self.logger.log(block_type, detail)
        if self.callback:
            self.callback(*result)


# ============ Hosts拦截器 ============
class HostsBlocker:
    """Hosts文件拦截器"""
    
    MARKER_START = "# === 软件拦截卫士开始 ==="
    MARKER_END = "# === 软件拦截卫士结束 ==="
    
    def __init__(self, config, logger, callback=None):
        self.config = config
        self.logger = logger
        self.callback = callback
        self.backup_manager = HostsBackupManager(logger, callback)
    
    def update_hosts(self, force=False):
        """更新Hosts文件"""
        try:
            if HOSTS_FILE.exists():
                file_size = HOSTS_FILE.stat().st_size
                if file_size > MAX_HOSTS_SIZE:
                    self._log("Hosts拦截", f"Hosts文件过大({file_size/1024:.1f}KB)，建议清理")
                    return False
            
            if self.config.get("settings.hosts_backup_before_update", True):
                self.backup_manager.create_backup()
            
            if HOSTS_FILE.exists():
                with open(HOSTS_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            else:
                content = ""
            
            existing_domains = self._get_existing_blocked_domains(content)
            whitelist = self.config.get("whitelist.domains", [])
            blacklist = self.config.get("blacklist.domains", [])  # 新增：黑名单域名
            ad_servers = self.config.get("ad_servers", [])
            
            # 黑名单优先：将黑名单添加到拦截列表
            all_servers = ad_servers + [f"0.0.0.0 {domain}" for domain in blacklist]
            
            new_domains = []
            skipped_domains = []
            whitelisted_domains = []
            
            for server in all_servers:
                domain = self._extract_domain(server)
                
                if not domain:
                    continue
                
                # 检查黑名单优先级（黑名单中的域名即使同时在白名单中也要拦截，但用户明确添加到白名单的除外）
                if domain in whitelist and domain not in blacklist:
                    whitelisted_domains.append(domain)
                    continue
                
                if domain in existing_domains and not force:
                    skipped_domains.append(domain)
                    continue
                
                new_domains.append(server)
            
            if not new_domains and not force:
                self._log("Hosts拦截", f"所有域名已拦截，跳过写入 ({len(skipped_domains)}个已存在)")
                return True
            
            content = self._remove_old_rules(content)
            
            # 合并现有域名为列表
            existing_list = list(existing_domains.values()) if not force else []
            all_domains = existing_list + new_domains
            
            seen = set()
            unique_domains = []
            for domain_line in all_domains:
                domain = self._extract_domain(domain_line)
                if domain and domain not in seen:
                    # 如果域名在黑名单中，强制添加；如果在白名单中且不在黑名单，则跳过
                    if domain in whitelist and domain not in blacklist:
                        continue
                    seen.add(domain)
                    unique_domains.append(domain_line)
            
            max_domains = 5000
            if len(unique_domains) > max_domains:
                self._log("Hosts拦截", f"域名数量超限({len(unique_domains)})，只保留前{max_domains}个")
                unique_domains = unique_domains[:max_domains]
            
            if unique_domains:
                new_rules = f"\n{self.MARKER_START}\n"
                new_rules += "# 本段由软件拦截卫士自动生成，请勿手动修改\n"
                new_rules += f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                new_rules += f"# 拦截域名数: {len(unique_domains)}\n"
                new_rules += "\n".join(unique_domains)
                new_rules += f"\n{self.MARKER_END}\n"
                content += new_rules
                
                with open(HOSTS_FILE, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self._log("Hosts拦截", f"成功更新Hosts，新增{len(new_domains)}个，共{len(unique_domains)}个域名")
                return True
            else:
                self._log("Hosts拦截", "没有需要拦截的域名")
                return True
            
        except PermissionError:
            self._log("Hosts拦截", "更新Hosts文件失败: 需要管理员权限")
        except Exception as e:
            self._log("Hosts拦截", f"更新Hosts文件失败: {str(e)}")
        
        return False
    
    def _get_existing_blocked_domains(self, content):
        """获取当前已拦截的域名"""
        domains = {}
        pattern = f"{re.escape(self.MARKER_START)}(.*?){re.escape(self.MARKER_END)}"
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            block_content = match.group(1)
            for line in block_content.strip().split('\n'):
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                domain = self._extract_domain(line)
                if domain:
                    domains[domain] = line
        
        return domains
    
    def _extract_domain(self, line):
        """从Hosts行中提取域名"""
        match = re.search(r'^(?:0\.0\.0\.0|127\.0\.0\.1)\s+(\S+)', line.strip())
        if match:
            return match.group(1).lower()
        
        if re.match(r'^[a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z0-9][-a-zA-Z0-9.]*$', line.strip()):
            return line.strip().lower()
        
        return None
    
    def _remove_old_rules(self, content):
        """移除旧的拦截规则"""
        pattern = f"\n*{re.escape(self.MARKER_START)}.*?{re.escape(self.MARKER_END)}\n*"
        return re.sub(pattern, "", content, flags=re.DOTALL)
    
    def clear_all_rules(self):
        """清除所有拦截规则"""
        try:
            if not HOSTS_FILE.exists():
                return True
            
            self.backup_manager.create_backup()
            
            with open(HOSTS_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            new_content = self._remove_old_rules(content)
            
            with open(HOSTS_FILE, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            self._log("Hosts拦截", "已清除所有拦截规则")
            return True
            
        except Exception as e:
            self._log("Hosts拦截", f"清除规则失败: {str(e)}")
            return False
    
    def get_hosts_stats(self):
        """获取Hosts文件统计信息"""
        try:
            if not HOSTS_FILE.exists():
                return {"exists": False}
            
            with open(HOSTS_FILE, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            existing = self._get_existing_blocked_domains(content)
            file_size = len(content)
            
            return {
                "exists": True,
                "size": file_size,
                "size_kb": f"{file_size / 1024:.1f}",
                "blocked_count": len(existing),
                "is_oversize": file_size > MAX_HOSTS_SIZE
            }
            
        except Exception as e:
            return {"exists": False, "error": str(e)}
    
    def _log(self, block_type, detail):
        """记录日志"""
        result = self.logger.log(block_type, detail)
        if self.callback:
            self.callback(*result)


# ============ 进程拦截器（含安装秒杀） ============
class ProcessBlocker:
    """进程拦截器 - 含安装进程秒杀功能"""
    
    def __init__(self, config, logger, callback=None):
        self.config = config
        self.logger = logger
        self.callback = callback
        self.running = False
        self.thread = None
        self.blocked_pids = set()
        self.killed_installers = set()
        self.lock = threading.Lock()
    
    def is_whitelisted(self, proc_name):
        """检查进程是否在白名单中"""
        whitelist = self.config.get("whitelist.processes", [])
        proc_lower = proc_name.lower()
        
        for white_proc in whitelist:
            if white_proc.lower() in proc_lower or proc_lower in white_proc.lower():
                return True
        
        # 保护正常软件
        protected = ['steam', 'github', 'huorong', 'uuaccelerator', 'uu.exe']
        for p in protected:
            if p in proc_lower:
                return True
        
        return False
    
    def is_blacklisted(self, proc_name):
        """检查进程是否在黑名单中（优先级最高）"""
        blacklist = self.config.get("blacklist.processes", [])
        proc_lower = proc_name.lower()
        
        for black_proc in blacklist:
            if black_proc.lower() in proc_lower or proc_lower in black_proc.lower():
                return True
        
        return False
    
    def is_installer(self, proc_name):
        """检查是否是安装程序"""
        install_keywords = self.config.get("software_list.install_killers", [])
        proc_lower = proc_name.lower()
        
        for keyword in install_keywords:
            if keyword.lower() in proc_lower:
                return True
        
        return False
    
    def is_blocked_process(self, proc_name):
        """检查是否是黑名单进程"""
        block_processes = self.config.get("software_list.block_processes", [])
        proc_lower = proc_name.lower()
        
        for block_name in block_processes:
            if block_name.lower() in proc_lower:
                return True
        
        return False
    
    def start(self):
        """启动进程监控"""
        if not self.config.get("settings.monitor_process", True):
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        self._log("进程拦截", "进程监控已启动（含安装秒杀）")
    
    def stop(self):
        """停止进程监控"""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=3)
        self._log("进程拦截", "进程监控已停止")
    
    def _monitor_loop(self):
        """监控循环"""
        interval = self.config.get("settings.check_interval", 2)
        
        while self.running:
            try:
                current_pids = set()
                for proc in psutil.process_iter(['pid', 'name', 'exe']):
                    try:
                        proc_name = proc.info['name']
                        pid = proc.info['pid']
                        
                        if not proc_name:
                            continue
                        
                        current_pids.add(pid)
                        
                        # 优先检查黑名单（优先级最高）
                        if self.is_blacklisted(proc_name):
                            if pid not in self.blocked_pids:
                                self._kill_process(proc, proc_name, "黑名单拦截")
                                with self.lock:
                                    self.blocked_pids.add(pid)
                            continue
                        
                        # 跳过白名单
                        if self.is_whitelisted(proc_name):
                            continue
                        
                        # 检查是否是安装程序
                        if self.is_installer(proc_name):
                            if pid not in self.killed_installers:
                                self._kill_installer(proc, proc_name)
                                with self.lock:
                                    self.killed_installers.add(pid)
                            continue
                        
                        # 检查是否是黑名单进程
                        if self.is_blocked_process(proc_name):
                            if pid not in self.blocked_pids:
                                self._kill_process(proc, proc_name, "进程拦截")
                                with self.lock:
                                    self.blocked_pids.add(pid)
                                    
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                # 清理已不存在的pid记录
                with self.lock:
                    self.blocked_pids = self.blocked_pids & current_pids
                    self.killed_installers = self.killed_installers & current_pids
                    
            except Exception as e:
                print(f"进程监控错误: {e}")
            
            time.sleep(interval)
    
    def _kill_installer(self, proc, proc_name):
        """杀死安装程序"""
        try:
            pid = proc.info['pid']
            self._log("安装秒杀", f"发现安装程序: {proc_name} (PID: {pid})，立即终止！")
            
            parent = psutil.Process(pid)
            
            # 强制杀死进程树
            for child in parent.children(recursive=True):
                try:
                    child.kill()
                except:
                    pass
            
            parent.kill()
            
            # 等待确认终止
            try:
                parent.wait(timeout=2)
            except:
                pass
            
            self._log("安装秒杀", f"已秒杀安装程序: {proc_name}")
            
            # 尝试删除安装文件
            try:
                exe_path = parent.exe()
                if exe_path and os.path.exists(exe_path):
                    time.sleep(0.3)
                    os.remove(exe_path)
                    self._log("文件清理", f"已删除安装包: {exe_path}")
            except:
                pass
                
        except Exception as e:
            self._log("安装秒杀", f"秒杀失败: {proc_name} - {str(e)}")
    
    def _kill_process(self, proc, proc_name, block_type="进程拦截"):
        """终止进程"""
        try:
            pid = proc.info['pid']
            self._log(block_type, f"发现可疑进程: {proc_name} (PID: {pid})，正在终止...")
            
            parent = psutil.Process(pid)
            for child in parent.children(recursive=True):
                try:
                    child.terminate()
                except:
                    pass
            
            parent.terminate()
            
            gone, alive = psutil.wait_procs([parent], timeout=3)
            if parent in alive:
                parent.kill()
            
            self._log(block_type, f"成功终止进程: {proc_name}")
            
            try:
                exe_path = parent.exe()
                if exe_path and os.path.exists(exe_path):
                    time.sleep(0.5)
                    os.remove(exe_path)
                    self._log("文件清理", f"删除进程文件: {exe_path}")
            except:
                pass
                
        except Exception as e:
            self._log(block_type, f"终止进程失败: {proc_name} - {str(e)}")
    
    def _log(self, block_type, detail):
        """记录日志"""
        result = self.logger.log(block_type, detail)
        if self.callback:
            self.callback(*result)


# ============ 注册表拦截器 ============
class RegistryBlocker:
    """注册表拦截器"""
    
    def __init__(self, config, logger, callback=None):
        self.config = config
        self.logger = logger
        self.callback = callback
    
    def check_and_clean(self):
        """检查并清理注册表启动项"""
        if not self.config.get("settings.monitor_registry", True):
            return
        
        try:
            import winreg
            
            block_keys = self.config.get("auto_run.block_keys", [])
            
            self._check_registry_key(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                block_keys
            )
            
            self._check_registry_key(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
                block_keys
            )
            
        except Exception as e:
            self._log("注册表拦截", f"检查注册表失败: {str(e)}")
    
    def _check_registry_key(self, root_key, sub_key, block_keys):
        """检查指定的注册表键"""
        import winreg
        
        try:
            with winreg.OpenKey(root_key, sub_key, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
                index = 0
                to_delete = []
                
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, index)
                        for block_key in block_keys:
                            if block_key.lower() in name.lower():
                                to_delete.append((name, value))
                                self._log("注册表拦截", f"发现可疑启动项: {name} = {value}")
                                break
                        index += 1
                    except OSError:
                        break
                
                for name, value in to_delete:
                    try:
                        winreg.DeleteValue(key, name)
                        self._log("注册表拦截", f"成功删除启动项: {name}")
                    except Exception as e:
                        self._log("注册表拦截", f"删除启动项失败: {name} - {str(e)}")
                        
        except Exception as e:
            pass
    
    def _log(self, block_type, detail):
        """记录日志"""
        result = self.logger.log(block_type, detail)
        if self.callback:
            self.callback(*result)


# ============ 文件监控处理器 ============
class FileMonitorHandler(FileSystemEventHandler):
    """文件监控处理器"""
    
    def __init__(self, config, logger, callback=None):
        self.config = config
        self.logger = logger
        self.callback = callback
        self.whitelist_processes = [p.lower() for p in config.get("whitelist.processes", [])]
        self.blacklist_processes = [p.lower() for p in config.get("blacklist.processes", [])]
    
    def is_whitelisted_file(self, file_name):
        """检查文件是否在白名单中"""
        file_lower = file_name.lower()
        
        # 保护正常软件相关文件
        protected = ['steam', 'github', 'huorong', 'uuaccelerator']
        for p in protected:
            if p in file_lower:
                return True
        
        return False
    
    def is_blacklisted_file(self, file_name):
        """检查文件是否在黑名单中"""
        file_lower = file_name.lower()
        
        # 检查黑名单关键词
        for proc in self.blacklist_processes:
            if proc.lower() in file_lower:
                return True
        
        return False
    
    def on_created(self, event):
        """文件创建事件"""
        if event.is_directory:
            return
        
        file_path = event.src_path
        file_name = os.path.basename(file_path)
        
        # 检查白名单
        if self.is_whitelisted_file(file_name):
            return
        
        # 优先检查黑名单
        if self.is_blacklisted_file(file_name):
            self._log("文件拦截", f"发现黑名单文件: {file_path}")
            
            if self.config.get("settings.auto_delete_files", True):
                try:
                    time.sleep(0.5)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        self._log("文件拦截", f"成功删除黑名单文件: {file_name}")
                except Exception as e:
                    self._log("文件拦截", f"删除黑名单文件失败: {file_name} - {str(e)}")
            return
        
        # 检查默认拦截列表
        block_keywords = self.config.get("file_monitor.block_file_keywords", [])
        
        for keyword in block_keywords:
            if keyword.lower() in file_name.lower():
                self._log("文件拦截", f"发现可疑文件: {file_path}")
                
                if self.config.get("settings.auto_delete_files", True):
                    try:
                        time.sleep(0.5)
                        if os.path.exists(file_path):
                            os.remove(file_path)
                            self._log("文件拦截", f"成功删除可疑文件: {file_name}")
                    except Exception as e:
                        self._log("文件拦截", f"删除文件失败: {file_name} - {str(e)}")
                
                break
    
    def _log(self, block_type, detail):
        """记录日志"""
        result = self.logger.log(block_type, detail)
        if self.callback:
            self.callback(*result)


# ============ 文件拦截器 ============
class FileBlocker:
    """文件拦截器"""
    
    def __init__(self, config, logger, callback=None):
        self.config = config
        self.logger = logger
        self.callback = callback
        self.observer = None
    
    def start(self):
        """启动文件监控"""
        if not self.config.get("settings.monitor_files", True):
            return
        
        try:
            self.observer = Observer()
            handler = FileMonitorHandler(self.config, self.logger, self.callback)
            
            monitor_paths = self.config.get("file_monitor.monitor_paths", [])
            
            for path_template in monitor_paths:
                path = os.path.expandvars(path_template)
                
                if os.path.exists(path):
                    try:
                        self.observer.schedule(handler, path, recursive=True)
                        self._log("文件监控", f"正在监控: {path}")
                    except Exception as e:
                        self._log("文件监控", f"监控路径失败 {path}: {str(e)}")
            
            self.observer.start()
            self._log("文件监控", "文件监控已启动")
            
        except Exception as e:
            self._log("文件监控", f"启动文件监控失败: {str(e)}")
    
    def stop(self):
        """停止文件监控"""
        if self.observer:
            try:
                self.observer.stop()
                self.observer.join(timeout=3)
                self._log("文件监控", "文件监控已停止")
            except Exception as e:
                self._log("文件监控", f"停止监控出错: {str(e)}")
    
    def _log(self, block_type, detail):
        """记录日志"""
        result = self.logger.log(block_type, detail)
        if self.callback:
            self.callback(*result)


# ============ Hosts管理窗口 ============
class HostsManagerWindow:
    """Hosts管理窗口"""
    
    def __init__(self, parent, hosts_blocker, logger):
        self.hosts_blocker = hosts_blocker
        self.logger = logger
        
        self.window = tk.Toplevel(parent)
        self.window.title("Hosts管理")
        self.window.geometry("600x450")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_ui()
        self.refresh_backup_list()
    
    def create_ui(self):
        """创建界面"""
        status_frame = tk.LabelFrame(self.window, text="当前状态", padx=10, pady=5)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.status_text = tk.Label(status_frame, text="正在获取...", justify=tk.LEFT)
        self.status_text.pack(anchor=tk.W)
        
        btn_frame = tk.Frame(self.window)
        btn_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(btn_frame, text="立即备份", command=self.backup_now).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="更新Hosts", command=self.update_hosts).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="清除所有规则", command=self.clear_rules).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="刷新列表", command=self.refresh_backup_list).pack(side=tk.LEFT, padx=2)
        
        list_frame = tk.LabelFrame(self.window, text="备份列表（双击还原）", padx=10, pady=5)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        columns = ("time", "size", "filename")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)
        
        self.tree.heading("time", text="备份时间")
        self.tree.heading("size", text="大小")
        self.tree.heading("filename", text="文件名")
        
        self.tree.column("time", width=150)
        self.tree.column("size", width=80)
        self.tree.column("filename", width=300)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.tree.bind("<Double-1>", self.on_restore)
        
        bottom_frame = tk.Frame(self.window)
        bottom_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(bottom_frame, text="删除选中备份", command=self.delete_selected).pack(side=tk.LEFT, padx=2)
        tk.Button(bottom_frame, text="关闭", command=self.window.destroy).pack(side=tk.RIGHT, padx=2)
        
        self.update_status()
    
    def update_status(self):
        """更新状态显示"""
        stats = self.hosts_blocker.get_hosts_stats()
        
        if stats.get("exists"):
            status = f"Hosts文件大小: {stats.get('size_kb', '0')} KB\n"
            status += f"已拦截域名数: {stats.get('blocked_count', 0)} 个\n"
            if stats.get("is_oversize"):
                status += "警告: Hosts文件过大，建议清理"
        else:
            status = "Hosts文件不存在或无法访问"
        
        self.status_text.config(text=status)
    
    def refresh_backup_list(self):
        """刷新备份列表"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        backups = self.hosts_blocker.backup_manager.get_backup_list()
        
        for backup in backups:
            self.tree.insert("", tk.END, values=(
                backup['time'],
                backup['size'],
                backup['filename']
            ), tags=(backup['path'],))
    
    def backup_now(self):
        """立即备份"""
        result = self.hosts_blocker.backup_manager.create_backup()
        if result:
            messagebox.showinfo("成功", "Hosts备份成功！")
            self.refresh_backup_list()
        else:
            messagebox.showerror("失败", "Hosts备份失败！")
    
    def update_hosts(self):
        """更新Hosts"""
        if self.hosts_blocker.update_hosts():
            messagebox.showinfo("成功", "Hosts更新成功！")
            self.update_status()
        else:
            messagebox.showerror("失败", "Hosts更新失败，请检查日志！")
    
    def clear_rules(self):
        """清除所有规则"""
        if messagebox.askyesno("确认", "确定要清除所有拦截规则吗？"):
            if self.hosts_blocker.clear_all_rules():
                messagebox.showinfo("成功", "已清除所有规则！")
                self.update_status()
            else:
                messagebox.showerror("失败", "清除规则失败！")
    
    def on_restore(self, event):
        """双击还原"""
        selected = self.tree.selection()
        if not selected:
            return
        
        item = selected[0]
        tags = self.tree.item(item, "tags")
        if not tags:
            return
        
        backup_path = tags[0]
        backup_name = self.tree.item(item, "values")[2]
        
        if messagebox.askyesno("确认", f"确定要还原到备份 [{backup_name}] 吗？"):
            if self.hosts_blocker.backup_manager.restore_backup(backup_path):
                messagebox.showinfo("成功", "Hosts还原成功！")
                self.update_status()
            else:
                messagebox.showerror("失败", "Hosts还原失败！")
    
    def delete_selected(self):
        """删除选中的备份"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("提示", "请先选择要删除的备份")
            return
        
        item = selected[0]
        tags = self.tree.item(item, "tags")
        if not tags:
            return
            
        backup_path = tags[0]
        backup_name = self.tree.item(item, "values")[2]
        
        if messagebox.askyesno("确认", f"确定要删除备份 [{backup_name}] 吗？"):
            if self.hosts_blocker.backup_manager.delete_backup(backup_path):
                messagebox.showinfo("成功", "备份已删除！")
                self.refresh_backup_list()
            else:
                messagebox.showerror("失败", "删除备份失败！")


# ============ 白名单管理窗口 ============
class WhitelistWindow:
    """白名单管理窗口"""
    
    def __init__(self, parent, config, logger):
        self.config = config
        self.logger = logger
        
        self.window = tk.Toplevel(parent)
        self.window.title("白名单管理")
        self.window.geometry("500x400")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_ui()
        self.refresh_list()
    
    def create_ui(self):
        """创建界面"""
        info_label = tk.Label(
            self.window, 
            text="白名单中的进程和域名不会被拦截\n支持通配符: *.example.com",
            justify=tk.CENTER,
            fg="gray"
        )
        info_label.pack(pady=5)
        
        # 进程白名单
        proc_frame = tk.LabelFrame(self.window, text="进程白名单", padx=5, pady=5)
        proc_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.proc_listbox = tk.Listbox(proc_frame, height=6)
        proc_scrollbar = tk.Scrollbar(proc_frame, orient=tk.VERTICAL, command=self.proc_listbox.yview)
        self.proc_listbox.config(yscrollcommand=proc_scrollbar.set)
        
        self.proc_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        proc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 域名白名单
        domain_frame = tk.LabelFrame(self.window, text="域名白名单", padx=5, pady=5)
        domain_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.domain_listbox = tk.Listbox(domain_frame, height=6)
        domain_scrollbar = tk.Scrollbar(domain_frame, orient=tk.VERTICAL, command=self.domain_listbox.yview)
        self.domain_listbox.config(yscrollcommand=domain_scrollbar.set)
        
        self.domain_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        domain_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 添加区域
        add_frame = tk.Frame(self.window, padx=10, pady=5)
        add_frame.pack(fill=tk.X)
        
        tk.Label(add_frame, text="进程:").pack(side=tk.LEFT)
        self.proc_entry = tk.Entry(add_frame, width=15)
        self.proc_entry.pack(side=tk.LEFT, padx=2)
        tk.Button(add_frame, text="添加进程", command=self.add_proc).pack(side=tk.LEFT, padx=2)
        
        tk.Label(add_frame, text="域名:").pack(side=tk.LEFT, padx=(10, 0))
        self.domain_entry = tk.Entry(add_frame, width=15)
        self.domain_entry.pack(side=tk.LEFT, padx=2)
        tk.Button(add_frame, text="添加域名", command=self.add_domain).pack(side=tk.LEFT, padx=2)
        
        # 按钮区域
        btn_frame = tk.Frame(self.window, padx=10, pady=5)
        btn_frame.pack(fill=tk.X)
        
        tk.Button(btn_frame, text="删除选中进程", command=self.remove_proc).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="删除选中域名", command=self.remove_domain).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="刷新", command=self.refresh_list).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="关闭", command=self.window.destroy).pack(side=tk.RIGHT, padx=2)
    
    def refresh_list(self):
        """刷新列表"""
        self.proc_listbox.delete(0, tk.END)
        self.domain_listbox.delete(0, tk.END)
        
        proc_whitelist = self.config.get("whitelist.processes", [])
        domain_whitelist = self.config.get("whitelist.domains", [])
        
        for proc in proc_whitelist:
            self.proc_listbox.insert(tk.END, proc)
        
        for domain in domain_whitelist:
            self.domain_listbox.insert(tk.END, domain)
    
    def add_proc(self):
        """添加进程白名单"""
        proc = self.proc_entry.get().strip()
        
        if not proc:
            messagebox.showwarning("提示", "请输入进程名")
            return
        
        whitelist = self.config.get("whitelist.processes", [])
        
        if proc in whitelist:
            messagebox.showinfo("提示", "该进程已在白名单中")
            return
        
        whitelist.append(proc)
        self.config.set("whitelist.processes", whitelist)
        
        self.proc_entry.delete(0, tk.END)
        self.refresh_list()
        
        self.logger.log("白名单", f"添加进程: {proc}")
        messagebox.showinfo("成功", f"已添加 {proc} 到白名单")
    
    def add_domain(self):
        """添加域名白名单"""
        domain = self.domain_entry.get().strip().lower()
        
        if not domain:
            messagebox.showwarning("提示", "请输入域名")
            return
        
        whitelist = self.config.get("whitelist.domains", [])
        
        if domain in whitelist:
            messagebox.showinfo("提示", "该域名已在白名单中")
            return
        
        whitelist.append(domain)
        self.config.set("whitelist.domains", whitelist)
        
        self.domain_entry.delete(0, tk.END)
        self.refresh_list()
        
        self.logger.log("白名单", f"添加域名: {domain}")
        messagebox.showinfo("成功", f"已添加 {domain} 到白名单")
    
    def remove_proc(self):
        """删除进程白名单"""
        selected = self.proc_listbox.curselection()
        if not selected:
            messagebox.showinfo("提示", "请先选择要删除的进程")
            return
        
        proc = self.proc_listbox.get(selected[0])
        
        whitelist = self.config.get("whitelist.processes", [])
        if proc in whitelist:
            whitelist.remove(proc)
            self.config.set("whitelist.processes", whitelist)
            self.refresh_list()
            
            self.logger.log("白名单", f"移除进程: {proc}")
            messagebox.showinfo("成功", f"已从白名单移除 {proc}")
    
    def remove_domain(self):
        """删除域名白名单"""
        selected = self.domain_listbox.curselection()
        if not selected:
            messagebox.showinfo("提示", "请先选择要删除的域名")
            return
        
        domain = self.domain_listbox.get(selected[0])
        
        whitelist = self.config.get("whitelist.domains", [])
        if domain in whitelist:
            whitelist.remove(domain)
            self.config.set("whitelist.domains", whitelist)
            self.refresh_list()
            
            self.logger.log("白名单", f"移除域名: {domain}")
            messagebox.showinfo("成功", f"已从白名单移除 {domain}")


# ============ 黑名单管理窗口 ============
class BlacklistWindow:
    """黑名单管理窗口"""
    
    def __init__(self, parent, config, logger):
        self.config = config
        self.logger = logger
        
        self.window = tk.Toplevel(parent)
        self.window.title("黑名单管理")
        self.window.geometry("500x400")
        self.window.transient(parent)
        self.window.grab_set()
        
        self.create_ui()
        self.refresh_list()
    
    def create_ui(self):
        """创建界面"""
        info_label = tk.Label(
            self.window, 
            text="黑名单中的进程和域名将被强制拦截（优先级高于白名单）\n支持通配符: *.example.com",
            justify=tk.CENTER,
            fg="red"
        )
        info_label.pack(pady=5)
        
        # 进程黑名单
        proc_frame = tk.LabelFrame(self.window, text="进程黑名单", padx=5, pady=5)
        proc_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.proc_listbox = tk.Listbox(proc_frame, height=6)
        proc_scrollbar = tk.Scrollbar(proc_frame, orient=tk.VERTICAL, command=self.proc_listbox.yview)
        self.proc_listbox.config(yscrollcommand=proc_scrollbar.set)
        
        self.proc_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        proc_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 域名黑名单
        domain_frame = tk.LabelFrame(self.window, text="域名黑名单", padx=5, pady=5)
        domain_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.domain_listbox = tk.Listbox(domain_frame, height=6)
        domain_scrollbar = tk.Scrollbar(domain_frame, orient=tk.VERTICAL, command=self.domain_listbox.yview)
        self.domain_listbox.config(yscrollcommand=domain_scrollbar.set)
        
        self.domain_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        domain_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 添加区域
        add_frame = tk.Frame(self.window, padx=10, pady=5)
        add_frame.pack(fill=tk.X)
        
        tk.Label(add_frame, text="进程:").pack(side=tk.LEFT)
        self.proc_entry = tk.Entry(add_frame, width=15)
        self.proc_entry.pack(side=tk.LEFT, padx=2)
        tk.Button(add_frame, text="添加进程", command=self.add_proc).pack(side=tk.LEFT, padx=2)
        
        tk.Label(add_frame, text="域名:").pack(side=tk.LEFT, padx=(10, 0))
        self.domain_entry = tk.Entry(add_frame, width=15)
        self.domain_entry.pack(side=tk.LEFT, padx=2)
        tk.Button(add_frame, text="添加域名", command=self.add_domain).pack(side=tk.LEFT, padx=2)
        
        # 按钮区域
        btn_frame = tk.Frame(self.window, padx=10, pady=5)
        btn_frame.pack(fill=tk.X)
        
        tk.Button(btn_frame, text="删除选中进程", command=self.remove_proc).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="删除选中域名", command=self.remove_domain).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="刷新", command=self.refresh_list).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="关闭", command=self.window.destroy).pack(side=tk.RIGHT, padx=2)
    
    def refresh_list(self):
        """刷新列表"""
        self.proc_listbox.delete(0, tk.END)
        self.domain_listbox.delete(0, tk.END)
        
        proc_blacklist = self.config.get("blacklist.processes", [])
        domain_blacklist = self.config.get("blacklist.domains", [])
        
        for proc in proc_blacklist:
            self.proc_listbox.insert(tk.END, proc)
        
        for domain in domain_blacklist:
            self.domain_listbox.insert(tk.END, domain)
    
    def add_proc(self):
        """添加进程黑名单"""
        proc = self.proc_entry.get().strip()
        
        if not proc:
            messagebox.showwarning("提示", "请输入进程名")
            return
        
        blacklist = self.config.get("blacklist.processes", [])
        
        if proc in blacklist:
            messagebox.showinfo("提示", "该进程已在黑名单中")
            return
        
        blacklist.append(proc)
        self.config.set("blacklist.processes", blacklist)
        
        self.proc_entry.delete(0, tk.END)
        self.refresh_list()
        
        self.logger.log("黑名单", f"添加进程: {proc}")
        messagebox.showinfo("成功", f"已添加 {proc} 到黑名单")
    
    def add_domain(self):
        """添加域名黑名单"""
        domain = self.domain_entry.get().strip().lower()
        
        if not domain:
            messagebox.showwarning("提示", "请输入域名")
            return
        
        blacklist = self.config.get("blacklist.domains", [])
        
        if domain in blacklist:
            messagebox.showinfo("提示", "该域名已在黑名单中")
            return
        
        blacklist.append(domain)
        self.config.set("blacklist.domains", blacklist)
        
        self.domain_entry.delete(0, tk.END)
        self.refresh_list()
        
        self.logger.log("黑名单", f"添加域名: {domain}")
        messagebox.showinfo("成功", f"已添加 {domain} 到黑名单")
    
    def remove_proc(self):
        """删除进程黑名单"""
        selected = self.proc_listbox.curselection()
        if not selected:
            messagebox.showinfo("提示", "请先选择要删除的进程")
            return
        
        proc = self.proc_listbox.get(selected[0])
        
        blacklist = self.config.get("blacklist.processes", [])
        if proc in blacklist:
            blacklist.remove(proc)
            self.config.set("blacklist.processes", blacklist)
            self.refresh_list()
            
            self.logger.log("黑名单", f"移除进程: {proc}")
            messagebox.showinfo("成功", f"已从黑名单移除 {proc}")
    
    def remove_domain(self):
        """删除域名黑名单"""
        selected = self.domain_listbox.curselection()
        if not selected:
            messagebox.showinfo("提示", "请先选择要删除的域名")
            return
        
        domain = self.domain_listbox.get(selected[0])
        
        blacklist = self.config.get("blacklist.domains", [])
        if domain in blacklist:
            blacklist.remove(domain)
            self.config.set("blacklist.domains", blacklist)
            self.refresh_list()
            
            self.logger.log("黑名单", f"移除域名: {domain}")
            messagebox.showinfo("成功", f"已从黑名单移除 {domain}")


# ============ 主窗口 ============
class MainWindow:
    """主窗口"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.logger = Logger()
        
        self.process_blocker = None
        self.hosts_blocker = None
        self.registry_blocker = None
        self.file_blocker = None
        
        self.tray_icon = None
        self.running = True
        
        self.root = tk.Tk()
        self.root.title(f"{APP_NAME} v{APP_VERSION}")
        self.root.geometry("900x600")
        self.root.minsize(800, 500)
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.create_ui()
        self.init_blockers()
        
        if self.config.get("settings.auto_block_hosts", True):
            self.root.after(2000, self.update_hosts)
    
    def create_ui(self):
        """创建用户界面"""
        status_frame = tk.Frame(self.root, padx=10, pady=5)
        status_frame.pack(fill=tk.X)
        
        self.status_label = tk.Label(
            status_frame, 
            text="状态: 运行中 (管理员权限)", 
            font=("微软雅黑", 10, "bold"),
            fg="green"
        )
        self.status_label.pack(side=tk.LEFT)
        
        btn_frame = tk.Frame(status_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        # 开机自启按钮（动态显示）
        if self.is_startup_enabled():
            self.startup_btn = tk.Button(btn_frame, text="取消开机启动", command=self.toggle_startup)
        else:
            self.startup_btn = tk.Button(btn_frame, text="设置开机启动", command=self.toggle_startup)
        self.startup_btn.pack(side=tk.LEFT, padx=2)
        
        tk.Button(btn_frame, text="最小化到托盘", command=self.minimize_to_tray).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="退出软件", command=self.exit_app, fg="red").pack(side=tk.LEFT, padx=2)
        
        list_frame = tk.Frame(self.root, padx=10, pady=5)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(list_frame, text="拦截记录:", font=("微软雅黑", 9)).pack(anchor=tk.W)
        
        columns = ("time", "type", "detail")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        self.tree.heading("time", text="时间")
        self.tree.heading("type", text="类型")
        self.tree.heading("detail", text="详情")
        
        self.tree.column("time", width=120)
        self.tree.column("type", width=100)
        self.tree.column("detail", width=600)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        action_frame = tk.Frame(self.root, padx=10, pady=5)
        action_frame.pack(fill=tk.X)
        
        tk.Button(action_frame, text="手动检查", command=self.manual_check, width=12).pack(side=tk.LEFT, padx=2)
        tk.Button(action_frame, text="更新Hosts", command=self.update_hosts, width=12).pack(side=tk.LEFT, padx=2)
        tk.Button(action_frame, text="Hosts管理", command=self.show_hosts_manager, width=12).pack(side=tk.LEFT, padx=2)
        tk.Button(action_frame, text="白名单", command=self.show_whitelist, width=12).pack(side=tk.LEFT, padx=2)
        tk.Button(action_frame, text="黑名单", command=self.show_blacklist, width=12).pack(side=tk.LEFT, padx=2)
        tk.Button(action_frame, text="编辑规则", command=self.edit_config, width=12).pack(side=tk.LEFT, padx=2)
        tk.Button(action_frame, text="查看日志", command=self.view_logs, width=12).pack(side=tk.LEFT, padx=2)
        
        bottom_frame = tk.Frame(self.root, padx=10, pady=5)
        bottom_frame.pack(fill=tk.X)
        
        tk.Button(bottom_frame, text="关于", command=self.show_about).pack(side=tk.LEFT)
    
    def init_blockers(self):
        """初始化拦截器"""
        callback = self.on_block_event
        
        self.process_blocker = ProcessBlocker(self.config, self.logger, callback)
        self.hosts_blocker = HostsBlocker(self.config, self.logger, callback)
        self.registry_blocker = RegistryBlocker(self.config, self.logger, callback)
        self.file_blocker = FileBlocker(self.config, self.logger, callback)
        
        self.process_blocker.start()
        self.file_blocker.start()
        
        self.registry_blocker.check_and_clean()
    
    def on_block_event(self, timestamp, block_type, detail):
        """拦截事件回调"""
        if self.running and self.root:
            self.root.after(0, lambda: self.add_log_entry(timestamp, block_type, detail))
    
    def add_log_entry(self, timestamp, block_type, detail):
        """添加日志条目到列表"""
        try:
            self.tree.insert("", 0, values=(timestamp, block_type, detail))
            
            if len(self.tree.get_children()) > 500:
                self.tree.delete(self.tree.get_children()[-1])
        except Exception as e:
            print(f"添加日志条目失败: {e}")
    
    def manual_check(self):
        """手动检查"""
        self.add_log_entry(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "手动检查",
            "开始手动检查..."
        )
        
        if self.registry_blocker:
            self.registry_blocker.check_and_clean()
        
        self.add_log_entry(
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "手动检查",
            "手动检查完成"
        )
    
    def update_hosts(self):
        """更新Hosts"""
        if self.hosts_blocker:
            self.hosts_blocker.update_hosts()
    
    def show_hosts_manager(self):
        """显示Hosts管理窗口"""
        HostsManagerWindow(self.root, self.hosts_blocker, self.logger)
    
    def show_whitelist(self):
        """显示白名单管理窗口"""
        WhitelistWindow(self.root, self.config, self.logger)
    
    def show_blacklist(self):
        """显示黑名单管理窗口"""
        BlacklistWindow(self.root, self.config, self.logger)
    
    def edit_config(self):
        """编辑配置文件"""
        config_path = str(CONFIG_FILE)
        if os.path.exists(config_path):
            subprocess.Popen(["notepad.exe", config_path])
        else:
            messagebox.showerror("错误", "配置文件不存在！")
    
    def view_logs(self):
        """查看日志"""
        log_path = str(LOG_FILE)
        if os.path.exists(log_path):
            subprocess.Popen(["notepad.exe", log_path])
        else:
            messagebox.showinfo("提示", "日志文件不存在！")
    
    def show_about(self):
        """显示关于信息"""
        about_text = f"""{APP_NAME} v{APP_VERSION}

功能：拦截鲁大师、360、2345等流氓软件的自动安装和广告推送

新增功能：
• 强制管理员提权 - 双击直接管理员运行
• 安装进程秒杀 - 检测到安装程序立即杀死
• 白名单保护 - 不误杀正常软件
• 黑名单管理 - 强制拦截指定项目（优先级最高）
• Hosts自动备份与一键还原
• 智能规则校验，避免重复写入
• 完善的开机自启管理

白名单保护：
• 360急救箱系列 - 不拦截
• Steam - 不拦截
• GitHub - 不拦截
• 火绒安全 - 不拦截
• UU加速器 - 不拦截

黑名单功能：
• 用户可自定义强制拦截的进程和域名
• 黑名单优先级高于白名单
• 适用于拦截特定顽固软件

使用说明：
1. 程序已自动获取管理员权限
2. 自动监控并拦截可疑进程和安装程序
3. 点击【Hosts管理】可备份/还原Hosts
4. 点击【白名单/黑名单】可管理免拦截/必拦截项目
5. 点击【编辑规则】可自定义拦截规则
6. 点击【退出软件】可彻底关闭程序"""
        
        messagebox.showinfo("关于", about_text)
    
    def is_startup_enabled(self):
        """检查是否已设置开机自启"""
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_REG_KEY, 0, winreg.KEY_READ)
            try:
                value, _ = winreg.QueryValueEx(key, STARTUP_REG_NAME)
                winreg.CloseKey(key)
                exe_path = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]
                return exe_path in value
            except FileNotFoundError:
                winreg.CloseKey(key)
                return False
        except Exception:
            return False
    
    def toggle_startup(self):
        """切换开机自启状态"""
        try:
            import winreg
            
            exe_path = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]
            
            if self.is_startup_enabled():
                # 取消开机自启
                try:
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_REG_KEY, 0, winreg.KEY_WRITE)
                    winreg.DeleteValue(key, STARTUP_REG_NAME)
                    winreg.CloseKey(key)
                    messagebox.showinfo("成功", "已取消开机自启动！")
                    self.startup_btn.config(text="设置开机启动")
                    self.add_log_entry(
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "系统设置",
                        "已取消开机自启动"
                    )
                except FileNotFoundError:
                    pass
            else:
                # 设置开机自启
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_REG_KEY, 0, winreg.KEY_WRITE)
                winreg.SetValueEx(key, STARTUP_REG_NAME, 0, winreg.REG_SZ, f'"{exe_path}"')
                winreg.CloseKey(key)
                messagebox.showinfo("成功", "已添加到开机自启动！")
                self.startup_btn.config(text="取消开机启动")
                self.add_log_entry(
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "系统设置",
                    "程序已添加到开机启动"
                )
        except Exception as e:
            messagebox.showerror("错误", f"设置开机自启失败: {str(e)}")
    
    def minimize_to_tray(self):
        """最小化到托盘"""
        self.root.withdraw()
        self.create_tray_icon()
    
    def create_tray_icon(self):
        """创建托盘图标"""
        if self.tray_icon:
            return
        
        try:
            # 创建简单的图标
            image = Image.new('RGB', (64, 64), color='blue')
            draw = ImageDraw.Draw(image)
            draw.rectangle([16, 16, 48, 48], fill='white')
            draw.text((24, 24), "B", fill='blue')
            
            menu = pystray.Menu(
                pystray.MenuItem("显示主窗口", self.show_window),
                pystray.MenuItem("手动检查", lambda: self.root.after(0, self.manual_check)),
                pystray.MenuItem("更新Hosts", lambda: self.root.after(0, self.update_hosts)),
                pystray.MenuItem("退出软件", self.exit_app)
            )
            
            self.tray_icon = pystray.Icon("SoftwareBlocker", image, APP_NAME, menu)
            
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
        except Exception as e:
            print(f"创建托盘图标失败: {e}")
            self.show_window()
    
    def show_window(self):
        """显示主窗口"""
        self.root.deiconify()
        self.root.lift()
        self.root.focus_force()
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except:
                pass
            self.tray_icon = None
    
    def on_close(self):
        """窗口关闭事件 - 最小化到托盘"""
        self.minimize_to_tray()
    
    def exit_app(self):
        """彻底退出程序"""
        if messagebox.askyesno("确认退出", "确定要退出软件拦截卫士吗？\n退出后将不再拦截流氓软件！"):
            self.running = False
            
            # 停止所有拦截器
            if self.process_blocker:
                try:
                    self.process_blocker.stop()
                except:
                    pass
            
            if self.file_blocker:
                try:
                    self.file_blocker.stop()
                except:
                    pass
            
            # 停止托盘图标
            if self.tray_icon:
                try:
                    self.tray_icon.stop()
                except:
                    pass
            
            # 关闭窗口
            try:
                self.root.quit()
                self.root.destroy()
            except:
                pass
            
            # 强制退出
            os._exit(0)
    
    def run(self):
        """运行主循环"""
        try:
            self.root.mainloop()
        except Exception as e:
            print(f"主循环错误: {e}")
        finally:
            self.exit_app()


# ============ 主函数 ============
def main():
    """主函数"""
    try:
        app = MainWindow()
        app.run()
    except Exception as e:
        messagebox.showerror("错误", f"程序启动失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()