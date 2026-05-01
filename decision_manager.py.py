#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
软件拦截卫士 v2.2「一键替换版」
新增：首次见到 360 / 2345 时弹窗询问
 - 选「是」→ 仅拦广告域名，进程放行
 - 选「否」→ 立即静默卸载+进程拦截
决策结果缓存，可重置
"""

import os, sys, json, time, threading, subprocess, re, shutil, glob
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox

# ========== 管理员提权 ==========
def run_as_admin():
    try:
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            sys.exit(0)
    except:
        sys.exit(1)
run_as_admin()

# ========== 自动装依赖 ==========
def fix_deps():
    missing = []
    for p in ['psutil', 'watchdog', 'pystray', 'PIL']:
        try: __import__(p)
        except: missing.append(p)
    if missing:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing)
fix_deps()

import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pystray
from PIL import Image, ImageDraw

# ========== 决策管理（内嵌） ==========
DECISION_FILE = Path(__file__).parent / "config" / "decision.json"
def _load_decision():
    try: return json.loads(DECISION_FILE.read_text('utf-8'))
    except: return {}
def _save_decision(data):
    DECISION_FILE.parent.mkdir(exist_ok=True)
    DECISION_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), 'utf-8')

def ask_and_act(name, logger):
    root = tk.Tk(); root.withdraw()
    allow = messagebox.askyesno(f"{name} 安装确认",
        "检测到《{}》正在运行/安装。\n• 选【是】→ 仅拦截广告域名\n• 选【否】→ 立即静默卸载".format(name))
    root.destroy()
    dec = _load_decision(); dec[name.lower()] = allow; _save_decision(dec)
    if allow:
        logger.log("决策放行", f"允许 {name}，仅堵广告域名")
    else:
        logger.log("用户拒绝", f"开始静默卸载 {name}")
        for exe in [r"C:\Program Files (x86)\360\360Safe\uninst.exe",
                    r"C:\Program Files\360\360Safe\uninst.exe",
                    r"C:\Program Files (x86)\360\360se6\uninst.exe",
                    r"C:\Program Files\360\360zip\uninst.exe"]:
            if os.path.isfile(exe):
                subprocess.Popen([exe, "/quiet"], stdout=subprocess.DEVNULL)
                break

# ========== 原配置略做追加 ==========
APP_NAME = "软件拦截卫士"; APP_VERSION="2.2"
CONFIG_DIR = Path(__file__).parent / "config"
CONFIG_FILE = CONFIG_DIR / "config.json"
LOG_FILE = CONFIG_DIR / "block_log.txt"
BACKUP_DIR = Path(__file__).parent / "backup"
HOSTS_FILE = Path(r"C:\Windows\System32\drivers\etc\hosts")
CONFIG_DIR.mkdir(exist_ok=True); BACKUP_DIR.mkdir(exist_ok=True)

class ConfigManager:
    DEFAULT_CONFIG = {
        "software_list": {
            "block_processes":[
                "鲁大师.exe","LDS.exe","LDSGui.exe","LDSGameMaster.exe",
                "360installer.exe","360Safe.exe","360rp.exe","360sd.exe",
                "2345Explorer.exe","2345看图王.exe","2345安全卫士.exe"
            ],
            "install_killers":["360setup","2345setup","ludashi"]
        },
        "whitelist":{"processes":[],"domains":[]},
        "blacklist":{"processes":[],"domains":[]},
        "ad_servers":["0.0.0.0 360.cn","0.0.0.0 2345.com"]
    }
    def __init__(self): self.cfg=self._load()
    def _load(self):
        if CONFIG_FILE.exists():
            try: return json.loads(CONFIG_FILE.read_text('utf-8'))
            except: pass
        CONFIG_FILE.write_text(json.dumps(self.DEFAULT_CONFIG,ensure_ascii=False,indent=2),'utf-8')
        return self.DEFAULT_CONFIG.copy()
    def get(self,key,d=None): v=self.cfg; k=key.split('.')
    def set(self,key,val): ... # 略

class Logger:
    def log(self,typ,txt):
        t=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_FILE,"a",encoding="utf-8") as f: f.write(f"[{t}] [{typ}] {txt}\n")
        return t,typ,txt

# ========== Host Blocker 简版 ==========
class HostsBlocker:
    def __init__(self,cfg,logger):
        self.cfg=cfg; self.logger=logger
    def update_hosts(self):
        try:
            lines=HOSTS_FILE.read_text('utf-8', errors='ignore')
            if "#卫士封" not in lines:
                HOSTS_FILE.write_text(lines+"\n#卫士封\n"+'\n'.join(self.cfg.get("ad_servers",[])))
                self.logger.log("Hosts","已追加广告域名")
        except: self.logger.log("Hosts","Hosts写入失败")

# ========== 进程/安装拦截 ==========
class ProcessBlocker(threading.Thread):
    def __init__(self,cfg,logger):
        super().__init__(daemon=True)
        self.cfg=cfg; self.logger=logger; self.cache=set()
    def run(self):
        while True:
            for p in psutil.process_iter(['pid','name']):
                try:
                    nm=p.info['name']
                    # 决策流程
                    dec=_load_decision().get(nm.lower())
                    if dec is None and any(k in nm.lower() for k in ["360","2345"]):
                        ask_and_act(nm,self.logger); continue
                    if dec is True: continue
                    # 黑名单
                    blk=self.cfg.get("software_list.block_processes",[])
                    if any(b.lower() in nm.lower() for b in blk):
                        self.logger.log("拦截",f"杀进程 {nm}")
                        p.kill()
                        p.wait(timeout=2)
                except: pass
            time.sleep(2)

# ========== 主窗口极简 ==========
class MainWindow:
    def __init__(self):
        self.cfg=ConfigManager(); self.logger=Logger()
        self.blocker=ProcessBlocker(self.cfg,self.logger)
        self.blocker.start()
        HostsBlocker(self.cfg,self.logger).update_hosts()
        # 窗口 UI 用占位
        root=tk.Tk(); root.title("卫士运行中"); root.geometry("1x1"); root.after(100,root.withdraw)
        # 托盘菜单
        menu=pystray.Menu(
            pystray.MenuItem("关于", lambda: messagebox.showinfo("关于","卫士已运行")),
            pystray.MenuItem("重置360",lambda: DECISION_FILE.unlink(missing_ok=True)),
            pystray.MenuItem("退出",lambda: os._exit(0))
        )
        icon=pystray.Icon("guard",Image.new('RGB',(64,64),'blue'),"卫士",menu)
        threading.Thread(target=icon.run).start()
        root.mainloop()

if __name__=="__main__":
    MainWindow()