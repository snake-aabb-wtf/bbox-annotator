<div align="center">
  <h1>📦 BBox Annotator</h1>
  <p><strong>轻量级图片标注工具 · Lightweight Image Bounding Box Annotator</strong></p>
  <p>
    <img src="https://img.shields.io/badge/python-3.8%20~%203.12-blue.svg">
    <img src="https://img.shields.io/badge/license-MIT-green.svg">
  </p>
  <p>拖拽标框 · 滚轮缩放 · 一键导出 YOLO 格式 · 纯本地零后端</p>
  <p>Drag to draw · Scroll to zoom · YOLO format export · Offline &amp; zero-backend</p>
</div>

---

## 📖 简介 | Introduction

**BBox Annotator** 是一个轻量级、纯本地的图片标注工具，专为物体检测任务设计。没有任何 Web 后端、数据库或云服务，启动即用。

**核心原则：** 一张图片标注完，存成一个同名 `.txt`，`cls cx cy w h` 归一化坐标，清晰可控。

- 🎯 **单类 / 多类标注** — 类别完全由你定义，启动时在设置窗口里添加（默认无预设类别）
- 🖱️ **鼠标画框** — 左键拖拽画框，右键点击删除，直观高效
- 🔍 **缩放 + 平移** — 滚轮缩放到像素级（5% ~ 2000%），中键 / Ctrl+左键拖拽平移
- 📁 **YOLO 格式原生支持** — 每张图片对应一个 `.txt`，坐标归一化到 `[0, 1]`
- 🌏 **中文界面** — 状态栏、快捷键帮助全部中文，设置窗口还内置「教程」按钮
- 🚀 **即开即用** — `start.ps1`（Windows）/ `start.sh`（Linux/macOS）一键启动，自动建 venv + 装依赖

---

**BBox Annotator** is a lightweight, offline image annotation tool built for object detection. No web server, no database, no cloud — just you and your images.

- 🎯 Single / multi-class annotation (you define the classes — no preset)
- 🖱️ Drag to draw boxes, right-click to delete
- 🔍 Zoom to pixel level & pan with middle mouse
- 📁 Native YOLO format (`cls cx cy w h`)
- 🚀 One-click launch via `start.ps1` (Windows) / `start.sh` (Linux/macOS)

---

## 🖼️ 功能一览 | Features

### 设置窗口（Tkinter）

| 功能 | 说明 |
|------|------|
| 选择图片 / 标签文件夹 | 浏览按钮一键选定；选图后标签目录自动填 `<图片目录>/labels` |
| 类别管理 | 每行一个类别，「添加类别 / 删除选中」增删，去重 |
| **教程按钮** | 位于「开始标注」左侧，点击弹出操作说明弹窗（鼠标 / 键盘快捷键一览） |
| 开始标注 | 校验通过后保存配置并进入 OpenCV 标注界面 |

### 标注界面（OpenCV 窗口）

| 功能 | 操作 |
|------|------|
| 画框 | 左键拖拽（宽高均 > 5px 才落框） |
| 删框 | 右键点击框内部 |
| 缩放 | 滚轮 (5% ~ 2000%)，以光标为中心 |
| 平移 | 中键拖拽 或 Ctrl+左键拖拽 |
| 下一张 | `D` / `→` |
| 上一张 | `A` / `←` |
| 保存 | `S`（开启 auto_save 时切图自动保存） |
| 撤销 | `Z`（仅撤最后一个框） |
| 清空 | `C` |
| 重置缩放 | `R` |
| 跳过 | `N`（不保存直接下一张） |
| 切换类别 | `1` ~ `9`（对应 classes 索引 0–8） |
| 帮助 | `H`（显示 / 隐藏帮助覆盖层） |
| 退出 | `Q` / `ESC` |

> ⚠️ 注意：`Q` / `ESC` 与 `N` 退出或跳过时**不会自动保存**当前改动，标完记得先按 `S` 或切图保存。

---

## 🚀 快速开始 | Quick Start

### 环境要求 | Requirements

- **Windows / Linux / macOS**（Windows 为一等公民；Linux/macOS 中文状态栏需调整字体路径，见下文）
- **Python 3.8 ~ 3.12**（依赖锁定 `numpy<2`，Python 3.13 上无预编译 wheel，请勿使用 3.13）
- 依赖：`opencv-python`、`numpy`、 `Pillow`（运行启动脚本会自动安装）

### 一键启动 | One-click Launch

**Windows**

```powershell
# 方式一：右键 start.ps1 →「使用 PowerShell 运行」
# 方式二：在 PowerShell 中执行（绕过执行策略限制）
powershell -ExecutionPolicy Bypass -File .\start.ps1
```

脚本会：创建 `venv/` → 检测并安装依赖 → 备份旧日志 → 以 UTF-8 启动 `main.py`。

**Linux / macOS**

```bash
chmod +x start.sh
./start.sh
```

### 手动运行 | Manual

```bash
cd bbox-annotator

# 创建并激活虚拟环境（建议 Python 3.12）
python3.12 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 启动（自动弹出设置窗口）
python main.py
```

**你的标注文件会保存在 `<图片目录>/labels/` 下**，每张图对应一个同名的 `.txt`。

### 标注文件格式 (YOLO)

```
<class_id> <cx> <cy> <width> <height>
```

所有坐标已归一化到 `[0, 1]`（相对原图宽高），保留 6 位小数。例：

```
0 0.515625 0.456250 0.125000 0.350000
```

坐标还原公式：

```
x1 = (cx - w/2) * img_w ;  y1 = (cy - h/2) * img_h
x2 = (cx + w/2) * img_w ;  y2 = (cy + h/2) * img_h
```

---

## 📁 项目结构 | Project Structure

```
bbox-annotator/
├── main.py            # 入口：启动设置窗口 → 进入标注界面
├── annotator.py       # 标注核心：渲染、鼠标/键盘交互、缩放平移、YOLO 读写
├── selector.py        # Tkinter 设置窗口（含「教程」按钮）
├── config.py          # 配置加载与保存（DEFAULT_CONFIG / load_config / save_config）
├── config.json        # 运行时状态文件（程序每次启动会覆盖，勿当模板维护）
├── requirements.txt   # Python 依赖（带版本上限）
├── start.ps1          # Windows 一键启动（PowerShell）
├── start.sh           # Linux/macOS 一键启动（Bash）
├── tests/             # 冒烟测试（pytest）
├── .github/           # CI 工作流（ubuntu-latest + xvfb 无头跑测试）
├── AGENTS.md          # 面向 AI 编程代理的项目说明书
├── LICENSE
└── README.md
```

---

## ⚙️ 配置 | Configuration

配置在程序启动时写入 `config.json`，也可直接编辑该文件或在设置窗口里修改。**注意：`config.json` 会被程序自动覆盖，真正的默认值在 `config.py` 的 `DEFAULT_CONFIG`。**

```json
{
  "classes": [],
  "window_w": 1280,
  "window_h": 720,
  "auto_save": true,
  "line_thickness": 2
}
```

| 键 | 类型 | 默认 | 含义 |
|----|------|------|------|
| `images_dir` | str | `""` | 图片文件夹（必填） |
| `labels_dir` | str | `""` | 标签输出目录；为空时回退为 `<images_dir>/labels` |
| `classes` | list[str] | `[]` | 类别名列表；索引即 YOLO `class_id` |
| `window_w` / `window_h` | int | `1280` / `720` | 窗口尺寸（像素） |
| `auto_save` | bool | `true` | 切图时自动保存 |
| `line_thickness` | int | `2` | 框线粗细 |
| `box_color` | [B,G,R] | `[0,255,0]` | 默认框颜色（OpenCV 用 BGR） |
| `preview_color` | [B,G,R] | `[0,255,255]` | 预览框颜色 |

---

## 🧪 测试与 CI | Tests & CI

仓库含 `pytest` 冒烟测试（`pytest.ini` + `tests/`），只验证「能导入、依赖装得上、纯函数不崩」，不会主动打开 GUI 窗口：

```bash
pip install -r requirements.txt pytest
python -m pytest -v
```

CI（`.github/workflows/ci.yml`）在 `push` / `PR` 到 `master` 时触发，于 `ubuntu-latest` 上用 `xvfb-run` 提供虚拟显示，无头跑全部测试（已预装 `python3-tk`、`libgl1`）。

---

## 🌏 跨平台中文显示

中文通过 PIL 桥接绘制（OpenCV 原生不支持中文），默认尝试 `msyh.ttc`。**非 Windows 平台**需手动把字体路径改成系统自带 CJK 字体（如 `~/.fonts/NotoSansCJK.ttc`），否则状态栏中文会显示为方框。

---

## 🤝 贡献 | Contributing

Issue 和 PR 都欢迎。核心改进方向：

- 多边形 / 关键点标注（YOLO-seg）
- 暗色 / 亮色主题切换
- 批量调整已有的框
- 多步撤销 / 重做
- 修复「退出 / 跳过不保存」行为

提交前请本地实跑一次 `main.py`，确认窗口能打开、画框与保存正常，且不要提交 `venv/`、`__pycache__/`、`*.log`。

---

## 📄 许可 | License

MIT © [snake-aabb-wtf](https://github.com/snake-aabb-wtf)
