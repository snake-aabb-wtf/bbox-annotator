@echo off
chcp 65001 >nul
title 标注工具 - 人体检测 (Annotator)
cd /d "%~dp0"

set VENV_DIR=venv

:: ── 选择兼容的 Python 解释器 ──
:: 项目依赖 numpy<2，而 numpy 1.x 没有 Python 3.13 的二进制轮子，
:: 因此虚拟环境必须用 Python 3.12 或更低版本来创建。
set PYTHON_EXE=python
set MAJ=0
set MIN=0
for /f "tokens=2,3 delims=. " %%A in ('"%PYTHON_EXE%" --version 2^>^&1') do (
    set MAJ=%%A
    set MIN=%%B
)
if %MAJ%==3 if %MIN% GTR 12 goto :need312
goto :havepy

:need312
echo [setup] 默认 python 版本过高，需要 Python 3.12 或更低，正在查找 ...
set "PYTHON_EXE="
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PYTHON_EXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if not defined PYTHON_EXE if exist "C:\Python312\python.exe" set "PYTHON_EXE=C:\Python312\python.exe"
if not defined PYTHON_EXE if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe" set "PYTHON_EXE=C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe"
if not defined PYTHON_EXE (
    echo [ERROR] 未找到 Python 3.12。请安装 Python 3.8~3.12 后重试。
    pause
    exit /b 1
)
echo [setup] 将使用 %PYTHON_EXE% 创建虚拟环境

:havepy

:: ── 检查 / 创建虚拟环境 ──
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo [setup] 正在创建虚拟环境 ...
    "%PYTHON_EXE%" -m venv %VENV_DIR%
    if errorlevel 1 (
        echo [ERROR] 创建虚拟环境失败！请确保已安装 Python 3.8~3.12
        pause
        exit /b 1
    )
    echo [setup] 虚拟环境已创建
) else (
    set VMAJ=0
    set VMIN=0
    for /f "tokens=2,3 delims=. " %%A in ('"%VENV_DIR%\Scripts\python.exe" --version 2^>^&1') do (
        set VMAJ=%%A
        set VMIN=%%B
    )
    if %VMAJ%==3 if %VMIN% GTR 12 (
        echo [setup] 现有虚拟环境 Python 版本不兼容，正在重建 ...
        rmdir /s /q "%VENV_DIR%"
        "%PYTHON_EXE%" -m venv %VENV_DIR%
    )
)

:: ── 安装依赖 ──
echo [setup] 检查依赖 ...
"%VENV_DIR%\Scripts\python.exe" -c "import cv2" 2>nul
if errorlevel 1 (
    echo [setup] 正在安装依赖 ^(opencv-python, numpy, Pillow^) ...
    "%VENV_DIR%\Scripts\python.exe" -m pip install -r requirements.txt -q
    if errorlevel 1 (
        echo [ERROR] 安装依赖失败！请检查网络连接
        pause
        exit /b 1
    )
    echo [setup] 依赖安装完成
) else (
    echo [setup] 依赖已就绪
)

:: ── 清旧日志 ──
if exist annotate.log (
    copy /Y annotate.log annotate.log.bak >nul 2>nul
    del annotate.log
)

:: ── 启动 ──
echo ========================================
echo    标注工具 - 人体检测
echo ========================================
echo  鼠标: 左键画框  右键删框  滚轮缩放  中键平移
echo  键盘: D下一张  A上一张  S保存  Z撤销
echo        C清空  R重置缩放  H帮助  Q退出
echo ========================================
echo  日志: %~dp0annotate.log
echo.

start "Annotator" "%VENV_DIR%\Scripts\python.exe" -X utf8 "%~dp0main.py"

echo 已启动，等待窗口 ...
timeout /t 2 /nobreak >nul
