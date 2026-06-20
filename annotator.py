"""
标注主界面 - 图片标注核心功能 (支持缩放/平移)
完全从零实现，无外部可视化依赖
"""
import cv2
import os
import numpy as np
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

# ── 工具函数 ──────────────────────────────────────────────

def cv2_to_pil(img):
    return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))


def pil_to_cv2(img):
    return cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)


def put_chinese_text(img, text, pos, font_size=20, color=(255, 255, 255)):
    """在 OpenCV 图像上绘制中文文字 (PIL 桥接)"""
    pil_img = cv2_to_pil(img)
    draw = ImageDraw.Draw(pil_img)
    try:
        font = ImageFont.truetype("msyh.ttc", font_size)
    except Exception:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", font_size)
        except Exception:
            font = ImageFont.load_default()
    draw.text(pos, text, font=font, fill=tuple(reversed(color)))
    return pil_to_cv2(pil_img)


# ── 框绘制 (替代 bbox_visualizer) ────────────────────────

def draw_bounding_box(img, bbox, color, thickness=2):
    """绘制单个边界框"""
    x1, y1, x2, y2 = [int(v) for v in bbox]
    cv2.rectangle(img, (x1, y1), (x2, y2), color, thickness)
    # 四角小标记 (更明显)
    length = min(12, (x2 - x1) // 4, (y2 - y1) // 4)
    if length > 4:
        for (cx, cy, dx, dy) in [
            (x1, y1, 1, 1), (x2, y1, -1, 1),
            (x1, y2, 1, -1), (x2, y2, -1, -1)
        ]:
            cv2.line(img, (cx, cy), (cx + dx * length, cy), color, thickness)
            cv2.line(img, (cx, cy), (cx, cy + dy * length), color, thickness)


def draw_label(img, text, bbox, bg_color, text_color=(0, 0, 0)):
    """在框上方绘制标签 (纯 cv2)"""
    x1, y1, _, _ = [int(v) for v in bbox]
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 0.5
    thickness = 1
    (tw, th), _ = cv2.getTextSize(text, font, font_scale, thickness)
    pad = 4
    label_bg_y1 = y1 - th - pad * 2
    if label_bg_y1 < 0:
        # 框太靠上，标签放在框内下边缘
        label_bg_y1 = y1
        label_y = y1 + th + pad
    else:
        label_y = y1 - pad
    cv2.rectangle(img, (x1, label_bg_y1), (x1 + tw + pad * 2, label_bg_y1 + th + pad * 2), bg_color, -1)
    cv2.putText(img, text, (x1 + pad, label_y + pad), font, font_scale, text_color, thickness)


# ── 帮助面板 ──────────────────────────────────────────────

HELP_TEXT = [
    ("鼠标操作", ""),
    ("左键拖拽", "画框"),
    ("右键点击框", "删除框"),
    ("滚轮", "缩放"),
    ("中键/Ctrl+左键拖拽", "平移"),
    ("", ""),
    ("键盘快捷键", ""),
    ("D / →", "下一张"),
    ("A / ←", "上一张"),
    ("S", "保存"),
    ("Q / ESC", "退出"),
    ("Z", "撤销上一个框"),
    ("C", "清空所有框"),
    ("N", "跳过当前图片"),
    ("R", "重置缩放"),
    ("H", "显示/隐藏帮助"),
    ("1-9", "切换类别"),
]


def draw_help_overlay(canvas):
    """绘制半透明帮助覆盖层"""
    overlay = canvas.copy()
    h, w = canvas.shape[:2]

    # 半透明深色背景
    cv2.rectangle(overlay, (0, 0), (w, h), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.75, canvas, 0.25, 0, canvas)

    # 标题
    canvas = put_chinese_text(canvas, "快捷键帮助", (w // 2 - 60, 30), font_size=26, color=(0, 255, 255))

    # 分两列
    left_x = w // 2 - 250
    right_x = w // 2 + 50
    y_start = 80
    line_h = 26

    # 先用 PIL 判断文字高度
    try:
        font_small = ImageFont.truetype("msyh.ttc", 16)
    except Exception:
        try:
            font_small = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 16)
        except Exception:
            font_small = ImageFont.load_default()

    pil_img = cv2_to_pil(canvas)
    draw = ImageDraw.Draw(pil_img)

    col1_y, col2_y = y_start, y_start
    mid = len(HELP_TEXT) // 2 + 1
    for i, (key, desc) in enumerate(HELP_TEXT):
        if i < mid:
            x_pos = left_x
            y_pos = col1_y
            col1_y += line_h
        else:
            x_pos = right_x
            y_pos = col2_y
            col2_y += line_h

        if key == "" and desc == "":
            continue
        if desc == "":
            # 分类标题
            draw.text((x_pos, y_pos), key, font=font_small, fill=(255, 255, 100))
        else:
            draw.text((x_pos, y_pos), key, font=font_small, fill=(100, 200, 255))
            tw = draw.textbbox((0, 0), key, font=font_small)[2] - draw.textbbox((0, 0), key, font=font_small)[0]
            draw.text((x_pos + tw + 20, y_pos), desc, font=font_small, fill=(200, 200, 200))

    canvas = pil_to_cv2(pil_img)
    return canvas


# ── 主标注函数 ────────────────────────────────────────────

def run_annotator(config):
    IMAGES_DIR = config["images_dir"]
    LABELS_DIR = config.get("labels_dir") or os.path.join(IMAGES_DIR, "labels")
    CLASSES = config["classes"]
    WINDOW_W = config.get("window_w", 1280)
    WINDOW_H = config.get("window_h", 720)
    AUTO_SAVE = config.get("auto_save", True)
    LINE_THICK = config.get("line_thickness", 2)

    WINDOW_NAME = "Annotator - Human Detection"
    LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "annotate.log")
    BAR_H = 50
    MIN_SCALE = 0.05
    MAX_SCALE = 20.0

    def log(msg):
        ts = datetime.now().strftime("%H:%M:%S.%f")[:12]
        line = f"[{ts}] {msg}"
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line + "\n")
            f.flush()

    log("=" * 50)
    log(f"标注工具启动 | 图片: {IMAGES_DIR} | 标签: {LABELS_DIR}")
    log(f"类别: {CLASSES}")

    images = sorted([f for f in os.listdir(IMAGES_DIR)
                     if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.webp'))])
    if not images:
        log("ERROR: 未找到图片")
        print("未找到图片！")
        return

    log(f"共 {len(images)} 张图片")
    os.makedirs(LABELS_DIR, exist_ok=True)

    # ── 状态 ──
    STATE = {
        "drawing": False,          # 正在画框
        "drag_start": (0, 0),      # 画框起点 (图像坐标)
        "preview": None,           # 预览框 (屏幕坐标)
        "bboxes": [],              # 边界框列表 [x1,y1,x2,y2] (图像坐标)
        "classes": [],             # 对应的类别索引
        "modified": False,
        "current_class": 0,

        # 缩放/平移
        "scale": 1.0,
        "fit_scale": 1.0,          # 适应窗口的缩放比
        "pan_x": 0,                # 图像左上角在画布上的 x 偏移
        "pan_y": 0,                # 图像左上角在画布上的 y 偏移
        "panning": False,          # 是否正在平移
        "pan_start_screen": (0, 0),# 平移起点 (屏幕坐标)
        "pan_start_offset": (0, 0),# 平移起点时的偏移量

        "show_help": False,
    }

    # ── 帮助函数 ──

    def _calc_fit_scale(img_w, img_h, canvas_w, canvas_h):
        """计算适应窗口的缩放比"""
        if img_w == 0 or img_h == 0:
            return 1.0
        return min(canvas_w / img_w, canvas_h / img_h)

    def _img_to_screen(ix, iy):
        """图像坐标 → 画布屏幕坐标"""
        return ix * STATE["scale"] + STATE["pan_x"], iy * STATE["scale"] + STATE["pan_y"]

    def _screen_to_img(sx, sy):
        """画布屏幕坐标 → 图像坐标"""
        return (sx - STATE["pan_x"]) / STATE["scale"], (sy - STATE["pan_y"]) / STATE["scale"]

    def _recenter(img_w, img_h, canvas_w, canvas_h):
        """将图像居中显示"""
        fit_s = _calc_fit_scale(img_w, img_h, canvas_w, canvas_h)
        STATE["fit_scale"] = fit_s
        STATE["scale"] = fit_s
        disp_w = int(img_w * fit_s)
        disp_h = int(img_h * fit_s)
        STATE["pan_x"] = (canvas_w - disp_w) // 2
        STATE["pan_y"] = (canvas_h - disp_h) // 2

    def _zoom_at(sx, sy, factor, img_w, img_h, canvas_w, canvas_h):
        """以屏幕坐标 (sx,sy) 为中心缩放"""
        old_scale = STATE["scale"]
        new_scale = np.clip(old_scale * factor, MIN_SCALE, MAX_SCALE)
        if new_scale == old_scale:
            return

        # 屏幕点对应的图像点 (在缩放前)
        img_x, img_y = _screen_to_img(sx, sy)

        STATE["scale"] = new_scale

        # 缩放后重新计算偏移，使图像点保持在屏幕同一位置
        STATE["pan_x"] = sx - img_x * new_scale
        STATE["pan_y"] = sy - img_y * new_scale

        # 边界限制 (防止完全移出视野)
        disp_w = img_w * new_scale
        disp_h = img_h * new_scale
        # 如果显示比画布小，居中
        if disp_w < canvas_w:
            STATE["pan_x"] = (canvas_w - disp_w) / 2
        else:
            STATE["pan_x"] = min(0, max(STATE["pan_x"], canvas_w - disp_w))
        if disp_h < canvas_h:
            STATE["pan_y"] = (canvas_h - disp_h) / 2
        else:
            STATE["pan_y"] = min(0, max(STATE["pan_y"], canvas_h - disp_h))

    # ── 标签加载/保存 ──

    def load_labels(filename):
        txt_path = os.path.join(LABELS_DIR, os.path.splitext(filename)[0] + ".txt")
        bboxes = []
        cls_list = []
        if os.path.exists(txt_path):
            img = cv2.imread(os.path.join(IMAGES_DIR, filename))
            if img is None:
                return bboxes, cls_list
            h, w = img.shape[:2]
            with open(txt_path) as f:
                for line in f:
                    parts = line.strip().split()
                    if len(parts) == 5:
                        cls_id, cx, cy, bw, bh = map(float, parts)
                        x1 = int((cx - bw / 2) * w)
                        y1 = int((cy - bh / 2) * h)
                        x2 = int((cx + bw / 2) * w)
                        y2 = int((cy + bh / 2) * h)
                        bboxes.append([x1, y1, x2, y2])
                        cls_list.append(int(cls_id))
            log(f"  加载标注: {filename} -> {len(bboxes)} boxes")
        return bboxes, cls_list

    def save_labels(filename, bboxes, cls_list, img_shape):
        h, w = img_shape[:2]
        txt_path = os.path.join(LABELS_DIR, os.path.splitext(filename)[0] + ".txt")
        with open(txt_path, "w") as f:
            for i, (x1, y1, x2, y2) in enumerate(bboxes):
                x1_, x2_ = min(x1, x2), max(x1, x2)
                y1_, y2_ = min(y1, y2), max(y1, y2)
                cx = (x1_ + x2_) / 2 / w
                cy = (y1_ + y2_) / 2 / h
                bw = (x2_ - x1_) / w
                bh = (y2_ - y1_) / h
                cls_id = cls_list[i] if i < len(cls_list) else 0
                f.write(f"{cls_id} {cx:.6f} {cy:.6f} {bw:.6f} {bh:.6f}\n")
        log(f"  保存: {txt_path} ({len(bboxes)} boxes)")

    def class_color(cls_id):
        colors = [
            (0, 255, 0), (255, 0, 0), (0, 0, 255),
            (255, 255, 0), (0, 255, 255), (255, 0, 255),
            (128, 255, 0), (0, 128, 255), (255, 128, 0),
        ]
        return colors[cls_id % len(colors)]

    # ── 鼠标回调 ──

    def mouse_callback(event, x, y, flags, param):
        img_h, img_w = param

        # 检查是否在图片显示区域 (排除下方状态栏)
        # 画布高度固定 = WINDOW_H, 图像区域 = WINDOW_H - BAR_H
        canvas_area_h = WINDOW_H - BAR_H
        if y >= canvas_area_h:
            return

        # ── 鼠标滚轮 ──
        if event == cv2.EVENT_MOUSEWHEEL:
            # flags 高16位编码了滚轮 delta (Windows: ±120)
            delta = (flags >> 16)
            factor = 1.15 if delta > 0 else 1 / 1.15
            canvas_area_h = WINDOW_H - BAR_H
            _zoom_at(x, y, factor, img_w, img_h, WINDOW_W, canvas_area_h)
            log(f"  [zoom] scale={STATE['scale']:.2f}")
            return

        # ── 中键平移 ──
        if event == cv2.EVENT_MBUTTONDOWN:
            STATE["panning"] = True
            STATE["pan_start_screen"] = (x, y)
            STATE["pan_start_offset"] = (STATE["pan_x"], STATE["pan_y"])
            return
        if event == cv2.EVENT_MBUTTONUP:
            STATE["panning"] = False
            return

        # ── Ctrl+左键平移 ──
        if event == cv2.EVENT_LBUTTONDOWN and (flags & cv2.EVENT_FLAG_CTRLKEY):
            STATE["panning"] = True
            STATE["pan_start_screen"] = (x, y)
            STATE["pan_start_offset"] = (STATE["pan_x"], STATE["pan_y"])
            return

        if event == cv2.EVENT_MOUSEMOVE and STATE["panning"]:
            dx = x - STATE["pan_start_screen"][0]
            dy = y - STATE["pan_start_screen"][1]
            STATE["pan_x"] = STATE["pan_start_offset"][0] + dx
            STATE["pan_y"] = STATE["pan_start_offset"][1] + dy
            return

        # ── 左键画框 (非Ctrl) ──
        if event == cv2.EVENT_LBUTTONDOWN and not (flags & cv2.EVENT_FLAG_CTRLKEY):
            STATE["drawing"] = True
            img_x, img_y = _screen_to_img(x, y)
            STATE["drag_start"] = (img_x, img_y)
            log(f"  [draw] 起点 ({img_x:.1f}, {img_y:.1f})")
            return

        if event == cv2.EVENT_MOUSEMOVE and STATE["drawing"]:
            sx, sy = STATE["drag_start"]
            img_x, img_y = _screen_to_img(x, y)
            x1, y1 = min(sx, img_x), min(sy, img_y)
            x2, y2 = max(sx, img_x), max(sy, img_y)
            # 预览框用屏幕坐标 (为了显示稳定)
            ps1, ps2 = _img_to_screen(x1, y1), _img_to_screen(x2, y2)
            STATE["preview"] = [int(ps1[0]), int(ps1[1]), int(ps2[0]), int(ps2[1])]
            return

        if event == cv2.EVENT_LBUTTONUP and STATE["drawing"]:
            STATE["drawing"] = False
            START = STATE["drag_start"]
            img_x, img_y = _screen_to_img(x, y)
            x1, y1 = min(START[0], img_x), min(START[1], img_y)
            x2, y2 = max(START[0], img_x), max(START[1], img_y)
            w, h = abs(x2 - x1), abs(y2 - y1)
            log(f"  [draw] 结束 ({x1:.0f},{y1:.0f})-({x2:.0f},{y2:.0f}) = {w:.0f}x{h:.0f}")
            if w > 5 and h > 5:
                STATE["bboxes"].append([int(x1), int(y1), int(x2), int(y2)])
                STATE["classes"].append(STATE["current_class"])
                STATE["modified"] = True
                log(f"  [draw] box added, total: {len(STATE['bboxes'])}")
            STATE["preview"] = None
            return

        # ── 右键删除框 ──
        if event == cv2.EVENT_RBUTTONDOWN:
            img_x, img_y = _screen_to_img(x, y)
            log(f"  [del] 点击 ({img_x:.0f}, {img_y:.0f})")
            for i, (bx1, by1, bx2, by2) in enumerate(STATE["bboxes"]):
                if bx1 <= img_x <= bx2 and by1 <= img_y <= by2:
                    STATE["bboxes"].pop(i)
                    if i < len(STATE["classes"]):
                        STATE["classes"].pop(i)
                    STATE["modified"] = True
                    log(f"  [del] 删除 box #{i+1}, 剩余: {len(STATE['bboxes'])}")
                    break

    # ── 渲染 ──

    def render(img, bboxes, cls_list, preview=None, img_name="", idx=0):
        img_h, img_w = img.shape[:2]
        canvas_area_h = WINDOW_H - BAR_H

        # 1. 创建画布
        canvas = np.zeros((WINDOW_H, WINDOW_W, 3), dtype=np.uint8)
        canvas[:] = (55, 55, 55)

        # 2. 缩放图像
        scaled_w = int(img_w * STATE["scale"])
        scaled_h = int(img_h * STATE["scale"])
        if scaled_w <= 0 or scaled_h <= 0:
            return canvas
        img_scaled = cv2.resize(img, (scaled_w, scaled_h), interpolation=cv2.INTER_LINEAR if STATE["scale"] >= 0.5 else cv2.INTER_AREA)

        # 3. 计算可见区域 (裁剪到画布内)
        pan_x_int = int(round(STATE["pan_x"]))
        pan_y_int = int(round(STATE["pan_y"]))

        # 图像在画布上的范围
        img_left = pan_x_int
        img_top = pan_y_int
        img_right = pan_x_int + scaled_w
        img_bottom = pan_y_int + scaled_h

        # 画布可见范围 (状态栏之上)
        canvas_right = WINDOW_W
        canvas_bottom = canvas_area_h

        # 计算重叠区域
        src_x1 = max(0, -img_left)               # 从缩放图的哪个 x 开始
        src_y1 = max(0, -img_top)                # 从缩放图的哪个 y 开始
        dst_x1 = max(0, img_left)                # 画布上的 x
        dst_y1 = max(0, img_top)                 # 画布上的 y

        copy_w = min(scaled_w - src_x1, canvas_right - dst_x1)
        copy_h = min(scaled_h - src_y1, canvas_bottom - dst_y1)

        if copy_w > 0 and copy_h > 0:
            canvas[dst_y1:dst_y1 + copy_h, dst_x1:dst_x1 + copy_w] = \
                img_scaled[src_y1:src_y1 + copy_h, src_x1:src_x1 + copy_w]

        # 4. 绘制边界框
        for i, bbox in enumerate(bboxes):
            cls_id = cls_list[i] if i < len(cls_list) else 0
            color = class_color(cls_id)
            cls_name = CLASSES[cls_id] if cls_id < len(CLASSES) else f"cls{cls_id}"

            # 框坐标从图像→屏幕
            sx1, sy1 = _img_to_screen(bbox[0], bbox[1])
            sx2, sy2 = _img_to_screen(bbox[2], bbox[3])
            screen_bbox = [int(sx1), int(sy1), int(sx2), int(sy2)]

            # 只绘制在画布可见区内的框
            if (sx2 < 0 or sy2 < 0 or sx1 > canvas_right or sy1 > canvas_bottom):
                continue

            draw_bounding_box(canvas, screen_bbox, color=color, thickness=LINE_THICK)
            draw_label(canvas, f"#{i+1} {cls_name}", screen_bbox, bg_color=color)

        # 5. 绘制预览框
        if preview is not None:
            px1, py1, px2, py2 = preview
            draw_bounding_box(canvas, (px1, py1, px2, py2), color=(0, 255, 255), thickness=2)

        # 6. 缩放指示器 (右下角)
        if STATE["scale"] != STATE["fit_scale"]:
            zoom_text = f"  {STATE['scale']:.0%}  "
            (zw, zh), _ = cv2.getTextSize(zoom_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            zx = canvas_right - zw - 15
            zy = canvas_bottom - zh - 15
            cv2.rectangle(canvas, (zx - 4, zy - 4), (zx + zw + 4, zy + zh + 4), (0, 0, 0), -1)
            cv2.putText(canvas, zoom_text, (zx, zy + zh), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

        # 7. 状态栏
        bar = np.zeros((BAR_H, WINDOW_W, 3), dtype=np.uint8)
        bar[:] = (35, 35, 40)

        n_boxes = len(STATE["bboxes"])
        mod = " *" if STATE["modified"] else ""
        progress = f"[{idx+1}/{len(images)}]"
        left_text = f"{progress} {img_name}{mod}  框:{n_boxes}  缩放:{STATE['scale']:.0%}"
        bar = put_chinese_text(bar, left_text, (10, 8), font_size=16, color=(255, 255, 255))

        right_text = f"类别: {CLASSES[STATE['current_class']]}  |  H=帮助"
        bar = put_chinese_text(bar, right_text, (WINDOW_W - 350, 8), font_size=16, color=(0, 255, 255))

        help_text = "D下一张 A上一张 S保存 Z撤销 C清空 R重置  Q退出"
        bar = put_chinese_text(bar, help_text, (10, 30), font_size=13, color=(160, 160, 160))

        canvas = np.vstack([canvas, bar])

        # 8. 帮助覆盖层
        if STATE["show_help"]:
            canvas = draw_help_overlay(canvas)

        return canvas

    # ── 主循环 ──
    def main_loop():
        nonlocal idx
        log(">>> 启动标注界面")
        idx = 0

        cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(WINDOW_NAME, WINDOW_W, WINDOW_H)

        while 0 <= idx < len(images):
            img_name = images[idx]
            log(f">>> [{idx+1}/{len(images)}] {img_name}")

            img = cv2.imread(os.path.join(IMAGES_DIR, img_name))
            if img is None:
                log(f"  ERROR: 无法读取 {img_name}")
                idx += 1
                continue

            h, w = img.shape[:2]

            # 加载已有标注
            STATE["bboxes"], STATE["classes"] = load_labels(img_name)
            STATE["modified"] = False
            STATE["preview"] = None
            STATE["drawing"] = False
            STATE["panning"] = False

            # 初始化缩放 (适应窗口)
            canvas_area_h = WINDOW_H - BAR_H
            _recenter(w, h, WINDOW_W, canvas_area_h)

            # 鼠标回调 (参数: 图像高宽, 用于画框边界判断)
            cv2.setMouseCallback(WINDOW_NAME, mouse_callback, (h, w))

            while True:
                canvas = render(img, STATE["bboxes"], STATE["classes"], STATE["preview"], img_name, idx)
                cv2.imshow(WINDOW_NAME, canvas)

                key = cv2.waitKey(30) & 0xFF

                if key in (ord("d"), 83):  # D / →
                    if STATE["modified"] and AUTO_SAVE:
                        save_labels(img_name, STATE["bboxes"], STATE["classes"], img.shape)
                    idx += 1
                    break

                elif key in (ord("a"), 81):  # A / ←
                    if STATE["modified"] and AUTO_SAVE:
                        save_labels(img_name, STATE["bboxes"], STATE["classes"], img.shape)
                    idx -= 1
                    break

                elif key == ord("z"):  # Z - 撤销
                    if STATE["bboxes"]:
                        STATE["bboxes"].pop()
                        if STATE["classes"]:
                            STATE["classes"].pop()
                        STATE["modified"] = True
                        log(">>> 撤销")

                elif key == ord("s"):  # S - 保存
                    save_labels(img_name, STATE["bboxes"], STATE["classes"], img.shape)
                    STATE["modified"] = False
                    log(f">>> 手动保存: {img_name}")

                elif key == ord("c"):  # C - 清空
                    if STATE["bboxes"]:
                        STATE["bboxes"] = []
                        STATE["classes"] = []
                        STATE["modified"] = True
                        log(">>> 清空所有框")

                elif key == ord("n"):  # N - 跳过
                    idx += 1
                    break

                elif key == ord("h"):  # H - 帮助
                    STATE["show_help"] = not STATE["show_help"]
                    log(f">>> 帮助: {'显示' if STATE['show_help'] else '隐藏'}")

                elif key == ord("r"):  # R - 重置缩放
                    canvas_area_h = WINDOW_H - BAR_H
                    _recenter(w, h, WINDOW_W, canvas_area_h)
                    log(f">>> 重置缩放 scale={STATE['scale']:.2f}")

                elif key in (ord("q"), 27):  # Q / ESC - 退出
                    cv2.destroyAllWindows()
                    log(">>> 用户退出")
                    return

                elif ord("1") <= key <= ord("9"):
                    cls_idx = key - ord("1")
                    if cls_idx < len(CLASSES):
                        STATE["current_class"] = cls_idx
                        log(f">>> 切换类别: {CLASSES[cls_idx]}")

        cv2.destroyAllWindows()
        log(">>> 全部完成")

    idx = 0
    main_loop()
