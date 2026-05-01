@echo off
chcp 65001 >nul
title 软件拦截卫士 - 管理员启动器

:: 检查是否以管理员身份运行
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [提示] 当前未以管理员身份运行，正在请求提升权限...
    echo.
    
    :: 使用PowerShell请求管理员权限重新运行
    powershell -Command "Start-Process '%~f0' -Verb runAs"
    exit /b
)

echo ========================================
echo      软件拦截卫士 - 管理员启动器
echo ========================================
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo [错误] 未检测到Python环境
    echo [提示] 请先安装Python 3.8或更高版本
    echo [下载] https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo [信息] Python环境检测通过
echo.

:: 检查主程序是否存在
if not exist "main.py" (
    echo [错误] 未找到 main.py
    echo [提示] 请确保此批处理文件与main.py在同一目录
    echo.
    pause
    exit /b 1
)

:: 安装依赖
echo [信息] 正在检查并安装依赖...
python -m pip install -r requirements.txt -q
if %errorLevel% neq 0 (
    echo [警告] 依赖安装可能出现问题，尝试继续运行...
)
echo.

echo [信息] 正在启动软件拦截卫士...
echo [信息] 启动时间: %date% %time%
echo.

:: 启动主程序
python main.py

echo.
echo [信息] 程序已退出
pause
