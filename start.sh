#!/usr/bin/env bash
# BBox Annotator — Linux/macOS 启动脚本
# 对应 Windows 的 start.ps1：建虚拟环境 + 装依赖 + 清旧日志 + 启动
# 用法: ./start.sh   （首次需 chmod +x start.sh）

set -euo pipefail

# 切到脚本所在目录
cd "$(dirname "$0")"

VENV_DIR="venv"

# ── 1. 检查 / 创建虚拟环境 ──
if [ ! -x "$VENV_DIR/bin/python" ]; then
  echo "[setup] 正在创建虚拟环境 ..."
  python3 -m venv "$VENV_DIR"
  echo "[setup] 虚拟环境已创建"
fi

# ── 2. 安装依赖 ──
echo "[setup] 检查依赖 ..."
if ! "$VENV_DIR/bin/python" -c "import cv2" 2>/dev/null; then
  echo "[setup] 正在安装依赖 (opencv-python, numpy, Pillow) ..."
  "$VENV_DIR/bin/python" -m pip install -r requirements.txt -q
  echo "[setup] 依赖安装完成"
else
  echo "[setup] 依赖已就绪"
fi

# ── 3. 备份并清空旧日志 ──
if [ -f annotate.log ]; then
  cp -f annotate.log annotate.log.bak
  : > annotate.log
fi

# ── 4. 启动 ──
echo "========================================"
echo "   标注工具 - BBox Annotator"
echo "========================================"
echo "  鼠标: 左键画框  右键删框  滚轮缩放  中键平移"
echo "  键盘: D下一张  A上一张  S保存  Z撤销"
echo "        C清空  R重置缩放  H帮助  Q退出"
echo "========================================"
echo "  日志: $(pwd)/annotate.log"
echo

exec "$VENV_DIR/bin/python" -X utf8 "$PWD/main.py"
