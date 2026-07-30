<div align="center">
  <h1>📦 BBox Annotator</h1>
  <p><strong>轻量级图片标注工具 · Lightweight Image Bounding Box Annotator</strong></p>
  <p>
    <img src="https://img.shields.io/badge/python-3.8+-blue.svg">
    <img src="https://img.shields.io/badge/license-MIT-green.svg">
  </p>
  <p>拖拽标框 · 滚轮缩放 · 一键导出 YOLO 格式 · 零依赖 (除 cv2 + PIL)</p>
  <p>Drag to draw · Scroll to zoom · YOLO format export · Zero bloat</p>
</div>

---

## 📖 简介 | Introduction

**BBox Annotator** 是一个轻量级、纯本地的图片标注工具，专门为物体检测任务设计。它没有任何 web 后端、数据库或云服务，启动即用。

**核心原则：** 一个文件标注完，存成一个 `.txt`，清晰可控。

- 🎯 **单类 / 多类标注** — 默认识别人，支持任意类别
- 🖱️ **鼠标画框** — 左键拖拽画框，右键点击删除，直观高效
- 🔍 **缩放 + 平移** — 滚轮缩放到像素级，中键拖拽平移，标大图 / 小目标无压力
- 📁 **YOLO 格式原生支持** — 每张图片对应一个 `.txt`，`cls cx cy w h` 归一化坐标
- 🌏 **中文界面** — 状态栏、快捷键帮助全部中文
- 🚀 **即开即用** — `start.ps1` 一键启动（PowerShell），自动处理环境

---

**BBox Annotator** is a lightweight, offline image annotation tool built for object detection. No web server, no database, no cloud — just you and your images.

- 🎯 Single / multi-class annotation (default: person)
- 🖱️ Drag to draw boxes, right-click to delete
- 🔍 Zoom to pixel level & pan with middle mouse
- 📁 Native YOLO format (`cls cx cy w h`)
- 🚀 One-click launch via `start.ps1` (PowerShell)

---

## 🖼️ 功能一览 | Features

| 功能 | 操作 |
|------|------|
| 画框 | 左键拖拽 |
| 删框 | 右键点击框内部 |
| 缩放 | 滚轮 (15% ~ 2000%) |
| 平移 | 中键拖拽 或 Ctrl+左键拖拽 |
| 下一张 | `D` / `→` |
| 上一张 | `A` / `←` |
| 保存 | `S` (自动保存可配置) |
| 撤销 | `Z` |
| 清空 | `C` |
| 重置缩放 | `R` |
| 跳过 | `N` |
| 切换类别 | `1` ~ `9` |
| 帮助 | `H` |
| 退出 | `Q` / `ESC` |

---

## 🚀 快速开始 | Quick Start

### 环境要求 | Requirements

- **Windows** (Linux/macOS 也能跑，但中文状态栏需要调字体路径)
- Python 3.8+
- 依赖：opencv-python, numpy, Pillow（或直接右键 start.ps1 用 PowerShell 运行自动装）

### 使用方法 | Usage

```bash
# 1. 右键 start.ps1 用 PowerShell 运行 (自动创建 venv + 安装依赖 + 启动)
#    或者手动：
python -m venv venv
venv\Scripts\pip install -r requirements.txt
venv\Scripts\python main.py

# 2. 在弹出的窗口中选择图片文件夹 + 设置类别
# 3. 开始标注！
```

**你的标注文件会保存在 `图片目录/labels/` 下**，每张图对应一个同名的 `.txt` 文件。

### 标注文件格式 (YOLO)

```
<class_id> <cx> <cy> <width> <height>
```

所有坐标已归一化到 `[0, 1]`。例：

```
0 0.515625 0.456250 0.125000 0.350000
```

---

## 📁 项目结构 | Project Structure

```
BBox-Annotator/
├── main.py              # 入口：文件夹选择 → 标注界面
├── annotator.py         # 标注核心：渲染、鼠标交互、缩放
├── selector.py          # Tkinter 文件夹选择器
├── config.py            # 配置加载/保存
├── config.json          # 持久化配置 (图片目录、类别等)
├── requirements.txt     # Python 依赖
├── start.ps1            # Windows 一键启动 (PowerShell)
├── LICENSE
└── README.md
```

---

## ⚙️ 配置 | Configuration

编辑 `config.json` 或直接在启动选择器里修改：

```json
{
  "classes": ["person"],
  "window_w": 1280,
  "window_h": 720,
  "auto_save": true,
  "line_thickness": 2
}
```

---

## 🤝 贡献 | Contributing

Issue 和 PR 都欢迎。核心改进方向：

- 多边形 / 关键点标注
- 暗色 / 亮色主题切换
- 批量调整已有的框

---

## 📄 许可 | License

MIT © [snake-aabb-wtf](https://github.com/snake-aabb-wtf)
