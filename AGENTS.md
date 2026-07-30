# AGENTS.md — BBox Annotator

面向 AI 编程代理（Coding Agent）的项目说明书。读这份文件即可安全地上手修改、扩展或排查本仓库，无需再去翻每个源文件猜意图。

> 一句话定位：**纯本地、零后端的轻量 YOLO 边界框标注工具**。没有 Web 服务、没有数据库、没有云依赖，启动即用。

---

## 1. 项目速览

| 项 | 说明 |
|----|------|
| 名称 | BBox Annotator（YOLO 图片标注工具） |
| 用途 | 为物体检测任务标注边界框，原生导出 YOLO `txt` 格式 |
| 语言 | Python 3.8+ |
| 核心依赖 | `opencv-python`(cv2)、`numpy`、`Pillow`(`PIL`)、`tkinter`(标准库) |
| 运行平台 | 桌面 GUI（OpenCV `highgui` 窗口 + Tkinter 选择器）；Windows 一等公民，Linux/macOS 可跑但中文状态栏需调字体 |
| 许可 | MIT |
| 入口 | `main.py` |

**核心原则**：每张图片标注完存成一个同名 `.txt`，归一化为 `cls cx cy w h`，清晰可控。

---

## 2. 仓库结构

```
bbox-annotator/
├── main.py            # 入口：启动 Tkinter 选择器 → 进入标注界面
├── annotator.py       # 标注核心：渲染、鼠标/键盘交互、缩放平移、YOLO 读写
├── selector.py        # Tkinter 文件夹/类别选择器 GUI
├── config.py          # 配置加载与保存（DEFAULT_CONFIG / load_config / save_config）
├── config.json        # 持久化配置（被 .gitignore 之外的常规文件，会被程序读写）
├── requirements.txt   # Python 依赖（带版本上限）
├── start.bat          # Windows 一键启动（建 venv + 装依赖 + 启动）
├── LICENSE
├── README.md
└── AGENTS.md          # 本文件
```

> ⚠️ 注意：`config.json` 会在程序运行时被**自动覆盖**（用户通过选择器保存时）。不要把它当作只读的“配置模板”——它是运行时状态文件。

---

## 3. 环境搭建与运行

### 3.1 一键启动（Windows 用户）
直接双击 `start.bat`。它会：
1. 若 `venv/` 不存在则创建虚拟环境；
2. 检测 `cv2` 是否可导入，缺失则 `pip install -r requirements.txt`；
3. 备份并清空旧的 `annotate.log`；
4. 以 `-X utf8` 启动 `main.py`。

### 3.2 手动运行（推荐给开发者）
```bash
cd bbox-annotator

# 创建并激活虚拟环境
python -m venv venv
venv\Scripts\pip install -r requirements.txt        # Windows
# source venv/bin/activate && pip install -r requirements.txt   # Linux/macOS

# 启动（会自动弹出 Tkinter 选择器）
venv\Scripts\python main.py
# 或：python main.py
```
> 提示：本机已有独立的 `E:\AI\.venv`（装了 torch/numpy），但**本项目不依赖 torch**，请按上面的 `venv` 流程装 `opencv-python/numpy/Pillow`，二者互不影响。

### 3.3 依赖版本约束（来自 `requirements.txt`）
```
opencv-python>=4.8.0,<5
numpy>=1.24.0,<2      # 注意上限 <2，numpy 2.x 未在此项目验证
Pillow>=10.0.0,<11
```
修改依赖版本前，务必在本地实跑一次 `main.py` 确认 GUI 正常，尤其 `opencv-python` 的 `highgui` 在目标平台可用。

---

## 4. 启动与数据流

```
main.py
  └─ FolderSelector()            # Tkinter 窗口
        ├─ 用户选择 图片目录 / 标签目录 / 类别
        ├─ save_config()         # 写回 config.json
        └─ mainloop() 结束（点“开始标注”后 destroy）
  └─ load_config()               # 读 config.json
  └─ run_annotator(config)       # 进入 OpenCV 标注主循环
        └─ 逐张图片：加载已有 .txt → 渲染 → 鼠标/键盘交互 → 保存
```

- `main.py` 通过 `sys.path.insert(0, 项目根目录)` 保证兄弟模块可被导入。
- 未选择有效 `images_dir` 时程序打印 `未选择图片目录，退出` 并return。
- 主循环 `cv2.waitKey(30)` 驱动；窗口名 `"Annotator - Human Detection"`。

---

## 5. 配置（`config.py` + `config.json`）

`config.py` 定义 `DEFAULT_CONFIG`，`load_config()` 用磁盘上的 `config.json` 覆盖默认值（深合并：仅覆盖存在的键）。

| 键 | 类型 | 默认 | 含义 |
|----|------|------|------|
| `images_dir` | str | `""` | 图片文件夹（必填） |
| `labels_dir` | str | `""` | 标签输出目录；为空时回退为 `<images_dir>/labels` |
| `classes` | list[str] | `["person"]` | 类别名列表；索引即 YOLO `class_id` |
| `window_w` | int | `1280` | 窗口宽（像素） |
| `window_h` | int | `720` | 窗口高（像素） |
| `auto_save` | bool | `true` | 切换图片时自动保存 |
| `show_labels` | bool | `true` | 是否绘制标签（声明但未在渲染中强依赖） |
| `line_thickness` | int | `2` | 框线粗细 |
| `box_color` | [B,G,R] | `[0,255,0]` | 默认框颜色（OpenCV 用 BGR） |
| `preview_color` | [B,G,R] | `[0,255,255]` | 预览框颜色 |

**修改约定**：
- 新增配置项 → 同时在 `DEFAULT_CONFIG` 和 `config.json` 中加上，并补到本表。
- 读取配置一律用 `config.get(key, default)`，不要直接 `config[key]`，避免老 `config.json` 缺键时 `KeyError`。
- 颜色是 **BGR** 顺序（OpenCV 习惯），不是 RGB。

---

## 6. 标注文件格式（YOLO）

每张图片在 `labels_dir` 下生成同名 `.txt`（仅改扩展名），每行一个框：

```
<class_id> <cx> <cy> <width> <height>
```

- 坐标**全部归一化到 `[0, 1]`**（相对原图像宽高）。
- 由 `save_labels()` 写出，保留 **6 位小数**（`{:.6f}`）。
- `load_labels()` 解析**恰好 5 个字段**的行；不足或超出的行被忽略。
- 坐标还原公式（图像像素）：
  ```
  x1 = (cx - w/2) * img_w ;  y1 = (cy - h/2) * img_h
  x2 = (cx + w/2) * img_w ;  y2 = (cy + h/2) * img_h
  ```
- 框在内部以像素 `[x1,y1,x2,y2]` 存储（图像坐标），保存时才转归一化。

---

## 7. 人机交互（实现位于 `annotator.py`）

### 鼠标
| 操作 | 行为 |
|------|------|
| 左键拖拽 | 画框（需宽高均 > 5px 才会落框） |
| 右键点击框内 | 删除该框（命中检测基于图像坐标） |
| 滚轮 | 以光标为中心缩放，`scale` 范围 `0.05 ~ 20.0`（即 5%–2000%） |
| 中键拖拽 / Ctrl+左键拖拽 | 平移画布 |

### 键盘
| 键 | 行为 |
|----|------|
| `D` / `→` | 下一张（开启 auto_save 时先存） |
| `A` / `←` | 上一张 |
| `S` | 手动保存 |
| `Z` | 撤销最后一个框 |
| `C` | 清空当前图片所有框 |
| `N` | 跳过当前图片（不保存直接下一张） |
| `R` | 重置缩放/居中 |
| `H` | 显示/隐藏帮助覆盖层 |
| `1`–`9` | 切换当前类别（对应 `classes` 索引 0–8） |
| `Q` / `ESC` | 退出 |

### 缩放/平移的内部模型（关键，改渲染前必读）
`annotator.py` 用一套坐标变换管理显示：
- `_img_to_screen(ix, iy)`：`ix*scale + pan_x`，`iy*scale + pan_y`
- `_screen_to_img(sx, sy)`：`(sx - pan_x)/scale`，`(sy - pan_y)/scale`
- `_recenter(...)`：按 `min(canvas/ img)` 计算 `fit_scale` 并居中
- `_zoom_at(sx, sy, factor, ...)`：以屏幕点为中心缩放，并保证图像不全部移出视野（小于画布时强制居中）
- 画布尺寸 = `WINDOW_H`，图像显示区 = `WINDOW_H - BAR_H`（底部 50px 是状态栏，鼠标事件在状态栏区域内被忽略）。

> 改动渲染/交互时，**务必保持图像坐标与屏幕坐标的双向变换一致**，否则画框、删框会错位。

---

## 8. 字体与国际化

- 中文通过 `put_chinese_text()` 用 PIL 桥接绘制（OpenCV 原生不支持中文）。
- 默认尝试字体 `msyh.ttc`，失败回退 `C:/Windows/Fonts/msyh.ttc`，再失败用 `ImageFont.load_default()`（无中文）。
- **非 Windows 平台**：需手动修改字体路径（如 `~/.fonts/NotoSansCJK.ttc` 或系统自带 CJK 字体），否则状态栏中文会变成方框/默认字体。
- 所有 UI 文案为中文；扩展多语言不是当前目标。

---

## 9. 日志

- 日志文件：`annotate.log`（项目根目录），由 `log()` 函数以 `append` 模式写入。
- `start.bat` 每次启动会把旧日志备份为 `annotate.log.bak` 再清空。
- `*.log`、`*.log.bak` 均被 `.gitignore` 忽略——**不要提交日志文件**。

---

## 10. 常见开发任务

| 任务 | 怎么做 |
|------|--------|
| 加新配置项 | 在 `config.py` 的 `DEFAULT_CONFIG` 加键 + 同步 `config.json` + 在 `run_annotator` 开头读出来 |
| 改类别默认 / 配色 | 改 `config.json`（运行时会被覆盖）或 `DEFAULT_CONFIG` |
| 支持多边形/关键点标注 | 在 `annotator.py` 扩展 `STATE` 与 `mouse_callback`/`render`，并新增 YOLO 变体导出 |
| 改标签保存精度 | 改 `save_labels()` 里的 `{:.6f}` |
| 调窗口默认尺寸 | 改 `config.json` 的 `window_w/window_h` |
| 跨平台字体修复 | 改 `put_chinese_text()` 与 `draw_help_overlay()` 的字体路径逻辑 |
| 本地验证 | 准备一个含若干 `.jpg/.png` 的文件夹，跑 `main.py`，标注几张后检查 `labels/*.txt` |

---

## 11. 提交与贡献约定

- 分支模型：默认 `master`，直接在此分支提交即可（本项目未强制 PR 分支流）。
- 提交信息：用简洁的中文或英文描述“做了什么”。
- 不要提交：`venv/`、`__pycache__/`、`*.log`、`*.log.bak`、`.vscode/`、`.idea/`、本地 `test_images/`——这些已在 `.gitignore` 中。
- 改动 GUI/交互后，务必本地实跑一次确认窗口能打开、画框/保存正常，再提交。
- Issue 与 PR 均欢迎；README“贡献”一节列了几个方向性改进（多边形/关键点、主题切换、批量调框）。

---

## 12. 已知限制 / 坑

1. `numpy` 上限锁 `<2`：`requirements.txt` 显式限制，升级到 2.x 前需回归测试。
2. `show_labels` 配置项声明但未在渲染逻辑中实际生效——如需实现，要去 `render()` 里接。
3. 字体硬编码 Windows 路径，跨平台需改代码。
4. 类别切换仅 `1`–`9`（最多 9 类）；超过 9 类无快捷键，需扩展键盘映射。
5. 撤销（`Z`）只撤最后一个框，不支持多步/重做。
6. `config.json` 是运行时状态文件，会被程序覆盖，不要把“出厂默认配置”期望寄托在它上面——真正的默认在 `config.py`。
