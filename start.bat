@echo off
chcp 65001 >nul
title 标注工具 - 人体检测 (Annotator)
cd /d "%~dp0"

set VENV_DIR=venv

:: ── 检查 / 创建虚拟环境 ──
if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo [setup] 正在创建虚拟环境 ...
    python -m venv %VENV_DIR%
    if errorlevel 1 (
        echo [ERROR] 创建虚拟环境失败！请确保已安装 Python 3.8+
        pause
        exit /b 1
    )
    echo [setup] 虚拟环境已创建
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
