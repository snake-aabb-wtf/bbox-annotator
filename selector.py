"""
GUI1: 文件夹选择器 - 选择图片目录和配置标注参数
"""
import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from config import load_config, save_config


class FolderSelector(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("YOLO 标注工具 - 项目设置")
        self.geometry("600x480")
        self.resizable(False, False)
        self.config = load_config()
        self._build_ui()
        self._load_to_ui()

    def _build_ui(self):
        main = ttk.Frame(self, padding=20)
        main.pack(fill=tk.BOTH, expand=True)

        # 图片目录
        ttk.Label(main, text="图片文件夹:", font=("微软雅黑", 11)).pack(anchor=tk.W)
        f1 = ttk.Frame(main)
        f1.pack(fill=tk.X, pady=(0, 10))
        self.img_dir_var = tk.StringVar()
        ttk.Entry(f1, textvariable=self.img_dir_var, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(f1, text="浏览...", command=self._browse_images).pack(side=tk.LEFT, padx=(8, 0))

        # 标签目录
        ttk.Label(main, text="标签输出文件夹:", font=("微软雅黑", 11)).pack(anchor=tk.W)
        f2 = ttk.Frame(main)
        f2.pack(fill=tk.X, pady=(0, 10))
        self.lbl_dir_var = tk.StringVar()
        ttk.Entry(f2, textvariable=self.lbl_dir_var, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(f2, text="浏览...", command=self._browse_labels).pack(side=tk.LEFT, padx=(8, 0))

        # 类别管理
        ttk.Label(main, text="标注类别 (每行一个):", font=("微软雅黑", 11)).pack(anchor=tk.W, pady=(10, 0))
        f3 = ttk.Frame(main)
        f3.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.class_listbox = tk.Listbox(f3, height=6, selectmode=tk.SINGLE)
        scrollbar = ttk.Scrollbar(f3, orient=tk.VERTICAL, command=self.class_listbox.yview)
        self.class_listbox.config(yscrollcommand=scrollbar.set)
        self.class_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        self.new_class_var = tk.StringVar()
        ttk.Entry(btn_frame, textvariable=self.new_class_var, width=20).pack(side=tk.LEFT)
        ttk.Button(btn_frame, text="添加类别", command=self._add_class).pack(side=tk.LEFT, padx=(8, 0))
        ttk.Button(btn_frame, text="删除选中", command=self._remove_class).pack(side=tk.LEFT, padx=(8, 0))

        # 预览
        self.preview_var = tk.StringVar(value="")
        ttk.Label(main, textvariable=self.preview_var, foreground="gray").pack(anchor=tk.W, pady=(5, 0))

        # 底部按钮
        bottom = ttk.Frame(main)
        bottom.pack(fill=tk.X, pady=(15, 0))
        ttk.Button(bottom, text="取消", command=self.destroy).pack(side=tk.RIGHT)
        ttk.Button(bottom, text="开始标注", command=self._start).pack(side=tk.RIGHT, padx=(0, 10))

    def _load_to_ui(self):
        self.img_dir_var.set(self.config.get("images_dir", ""))
        self.lbl_dir_var.set(self.config.get("labels_dir", ""))
        for cls in self.config.get("classes", []):
            self.class_listbox.insert(tk.END, cls)
        self._update_preview()

    def _browse_images(self):
        d = filedialog.askdirectory(title="选择图片文件夹")
        if d:
            self.img_dir_var.set(d)
            if not self.lbl_dir_var.get():
                self.lbl_dir_var.set(os.path.join(d, "labels"))
            self._update_preview()

    def _browse_labels(self):
        d = filedialog.askdirectory(title="选择标签输出文件夹")
        if d:
            self.lbl_dir_var.set(d)
            self._update_preview()

    def _add_class(self):
        name = self.new_class_var.get().strip()
        if name:
            items = list(self.class_listbox.get(0, tk.END))
            if name not in items:
                self.class_listbox.insert(tk.END, name)
                self.new_class_var.set("")
                self._update_preview()

    def _remove_class(self):
        sel = self.class_listbox.curselection()
        if sel:
            self.class_listbox.delete(sel[0])
            self._update_preview()

    def _update_preview(self):
        img_dir = self.img_dir_var.get()
        classes = list(self.class_listbox.get(0, tk.END))
        if img_dir and os.path.isdir(img_dir):
            exts = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')
            count = len([f for f in os.listdir(img_dir) if f.lower().endswith(exts)])
            self.preview_var.set(f"图片: {count} 张  |  类别: {', '.join(classes) if classes else '(无)'}")
        else:
            self.preview_var.set(f"类别: {', '.join(classes) if classes else '(无)'}")

    def _start(self):
        img_dir = self.img_dir_var.get().strip()
        lbl_dir = self.lbl_dir_var.get().strip()
        classes = list(self.class_listbox.get(0, tk.END))

        if not img_dir or not os.path.isdir(img_dir):
            messagebox.showerror("错误", "请选择有效的图片文件夹")
            return
        if not classes:
            messagebox.showerror("错误", "请至少添加一个标注类别")
            return
        if not lbl_dir:
            lbl_dir = os.path.join(img_dir, "labels")

        os.makedirs(lbl_dir, exist_ok=True)

        self.config["images_dir"] = img_dir
        self.config["labels_dir"] = lbl_dir
        self.config["classes"] = classes
        save_config(self.config)

        self.destroy()


def run_selector():
    app = FolderSelector()
    app.mainloop()
    return load_config()


if __name__ == "__main__":
    cfg = run_selector()
    print(f"图片目录: {cfg['images_dir']}")
    print(f"标签目录: {cfg['labels_dir']}")
    print(f"类别: {cfg['classes']}")
