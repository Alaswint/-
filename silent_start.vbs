' ============================================================
' 软件拦截卫士 - 静默后台运行脚本
' 功能：以管理员权限静默启动，无窗口显示
' ============================================================

Option Explicit

Dim WshShell, fso, scriptPath, pythonPath, mainPyPath
Dim objShellApp, isAdmin

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' 获取脚本所在目录
scriptPath = fso.GetParentFolderName(WScript.ScriptFullName)
mainPyPath = scriptPath & "\main.py"

' 检查main.py是否存在
If Not fso.FileExists(mainPyPath) Then
    WshShell.Popup "错误：未找到 main.py" & vbCrLf & _
                   "请确保此脚本与main.py在同一目录", _
                   10, "软件拦截卫士", 16
    WScript.Quit 1
End If

' 检查Python是否安装
Dim checkPython
On Error Resume Next
Set checkPython = WshShell.Exec("python --version")
If Err.Number <> 0 Then
    WshShell.Popup "错误：未检测到Python环境" & vbCrLf & _
                   "请先安装Python 3.8或更高版本", _
                   10, "软件拦截卫士", 16
    WScript.Quit 1
End If
On Error GoTo 0

' 使用Shell.Application以管理员权限静默启动
Set objShellApp = CreateObject("Shell.Application")
objShellApp.ShellExecute "python", "main.py", scriptPath, "runas", 0

Set WshShell = Nothing
Set fso = Nothing
Set objShellApp = Nothing

WScript.Quit 0
