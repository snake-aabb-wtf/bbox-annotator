"""
YOLO 标注工具 - 主入口
启动流程: 文件夹选择器 -> 点击"开始标注" -> 标注界面
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import load_config, save_config
from selector import FolderSelector
from annotator import run_annotator


def main():
    selector = FolderSelector()
    selector.mainloop()

    config = load_config()
    if not config.get("images_dir") or not os.path.isdir(config["images_dir"]):
        print("未选择图片目录，退出")
        return

    run_annotator(config)


if __name__ == "__main__":
    main()
