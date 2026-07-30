"""
annotator 模块冒烟测试
annotator.py 在导入时就 import cv2 / numpy / PIL，因此本文件同时验证了“依赖可导入”。
下面的纯函数都不需要打开任何 GUI 窗口，仅做数组/PIL 运算，适合在 CI 无头环境跑：
- cv2<->PIL 互转
- 画框 / 画标签 / 中文文字 / 帮助覆盖层
- HELP_TEXT 数据结构
"""
import numpy as np

import annotator


def _blank(h=100, w=100):
    return np.zeros((h, w, 3), dtype=np.uint8)


def test_module_level_api_present():
    for name in (
        "cv2_to_pil",
        "pil_to_cv2",
        "put_chinese_text",
        "draw_bounding_box",
        "draw_label",
        "draw_help_overlay",
        "run_annotator",
        "HELP_TEXT",
    ):
        assert hasattr(annotator, name)


def test_cv2_pil_roundtrip_preserves_shape():
    img = _blank(60, 80)
    pil = annotator.cv2_to_pil(img)
    back = annotator.pil_to_cv2(pil)
    assert back.shape == img.shape
    assert back.dtype == img.dtype


def test_draw_bounding_box_mutates_image():
    img = _blank(60, 60)
    before = img.copy()
    annotator.draw_bounding_box(img, (10, 10, 50, 50), color=(0, 255, 0), thickness=2)
    assert not np.array_equal(img, before)


def test_draw_label_mutates_image_in_place():
    # 注意：draw_label 是“就地修改”风格，返回 None（render() 里直接这么用）
    img = _blank(80, 200)
    before = img.copy()
    ret = annotator.draw_label(img, "person", (10, 30, 50, 50), bg_color=(0, 255, 0))
    assert ret is None
    assert not np.array_equal(img, before)


def test_put_chinese_text_runs_and_keeps_shape():
    img = _blank(80, 200)
    # 即便 Linux 上没有 msyh.ttc，也会回退到 ImageFont.load_default()，不应抛错
    out = annotator.put_chinese_text(img, "测试文字", (10, 10), font_size=20, color=(255, 255, 255))
    assert out.shape == img.shape


def test_draw_help_overlay_runs_and_keeps_shape():
    img = np.zeros((400, 600, 3), dtype=np.uint8)
    out = annotator.draw_help_overlay(img)
    assert out.shape == img.shape


def test_help_text_is_list_of_pairs():
    assert isinstance(annotator.HELP_TEXT, list)
    assert len(annotator.HELP_TEXT) > 0
    for entry in annotator.HELP_TEXT:
        assert isinstance(entry, tuple)
        assert len(entry) == 2
