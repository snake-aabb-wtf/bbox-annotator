"""
selector 模块冒烟测试
selector.py 顶部 `import tkinter`，整机无 tkinter 时整个模块无法导入，
因此用 importorskip 优雅跳过（CI 里已通过 apt 安装 python3-tk 保证可用）。

GUI 实例化测试：
- Linux 下需要一个显示（CI 用 xvfb-run 提供 DISPLAY），否则跳过；
- Windows / macOS 的 tkinter 不需要外部显示，直接跑。
"""
import os
import sys

import pytest

pytest.importorskip("tkinter")  # 没有 tkinter 则整文件跳过，不报红

import tkinter as tk  # noqa: E402  (上面已确认可导入)


def test_selector_module_api():
    import selector  # noqa: F401
    assert hasattr(selector, "FolderSelector")
    assert hasattr(selector, "run_selector")


def test_folder_selector_is_tk_subclass():
    import selector
    assert issubclass(selector.FolderSelector, tk.Tk)


def test_run_selector_is_callable():
    import selector
    assert callable(selector.run_selector)


# Linux 无显示时必须跳过；Win/macOS 不需要 DISPLAY
_needs_display = sys.platform == "linux" and not os.environ.get("DISPLAY")


@pytest.mark.skipif(_needs_display, reason="Linux 下需要显示（请用 xvfb-run 运行）")
def test_folder_selector_instantiates():
    import selector
    app = selector.FolderSelector()
    try:
        # 能建出来说明 _build_ui / _load_to_ui / load_config 都没在构造期崩
        assert app.winfo_exists()
        assert app.title()  # 设置了窗口标题
    finally:
        app.destroy()
