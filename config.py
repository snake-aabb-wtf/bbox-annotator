"""
配置管理模块
"""
import os
import json

DEFAULT_CONFIG = {
    "images_dir": "",
    "labels_dir": "",
    "classes": [],                 # 默认不预设类别，启动后由用户在界面中添加
    "window_w": 1280,
    "window_h": 720,
    "auto_save": True,
    "show_labels": True,
    "line_thickness": 2,
    "box_color": [0, 255, 0],
    "preview_color": [0, 255, 255],
}

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            saved = json.load(f)
        config = DEFAULT_CONFIG.copy()
        config.update(saved)
        return config
    return DEFAULT_CONFIG.copy()


def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
