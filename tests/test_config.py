"""
config 模块冒烟测试
- DEFAULT_CONFIG 的字段与默认值合理
- load_config 在“无文件 / 有文件”两种情况下行为正确
- save_config -> load_config 往返一致，且会与默认配置合并
注意：所有写操作都通过 monkeypatch 重定向到临时文件，绝不污染仓库里的 config.json。
"""
import json
import unittest.mock as mock

import config


EXPECTED_KEYS = (
    "images_dir",
    "labels_dir",
    "classes",
    "window_w",
    "window_h",
    "auto_save",
    "show_labels",
    "line_thickness",
    "box_color",
    "preview_color",
)


def test_default_config_has_all_keys():
    for key in EXPECTED_KEYS:
        assert key in config.DEFAULT_CONFIG


def test_default_config_contains_person_class():
    assert "person" in config.DEFAULT_CONFIG["classes"]


def test_load_config_returns_copy_of_default_when_no_file(tmp_path):
    fake = tmp_path / "config.json"
    with mock.patch.object(config, "CONFIG_FILE", str(fake)):
        cfg = config.load_config()
    # 内容相等，但必须是“副本”，不能返回模块里的单例
    assert cfg == config.DEFAULT_CONFIG
    assert cfg is not config.DEFAULT_CONFIG


def test_save_then_load_roundtrip(tmp_path):
    fake = tmp_path / "config.json"
    with mock.patch.object(config, "CONFIG_FILE", str(fake)):
        saved = dict(config.DEFAULT_CONFIG)
        saved["images_dir"] = "/tmp/imgs"
        saved["classes"] = ["cat", "dog"]
        config.save_config(saved)
        assert fake.exists()
        loaded = config.load_config()
    assert loaded["images_dir"] == "/tmp/imgs"
    assert loaded["classes"] == ["cat", "dog"]
    # 未显式保存的字段仍由默认补齐
    assert loaded["window_w"] == config.DEFAULT_CONFIG["window_w"]


def test_load_config_merges_saved_with_default(tmp_path):
    fake = tmp_path / "config.json"
    fake.write_text(json.dumps({"images_dir": "/x"}), encoding="utf-8")
    with mock.patch.object(config, "CONFIG_FILE", str(fake)):
        cfg = config.load_config()
    assert cfg["images_dir"] == "/x"
    # 其余字段回退默认
    assert cfg["classes"] == config.DEFAULT_CONFIG["classes"]
    assert cfg["auto_save"] is True


def test_saved_file_is_utf8_and_indented(tmp_path):
    fake = tmp_path / "config.json"
    with mock.patch.object(config, "CONFIG_FILE", str(fake)):
        config.save_config({"classes": ["人"]})
        text = fake.read_text(encoding="utf-8")
    assert "\n" in text  # indent=2 生效
    assert "人" in text   # ensure_ascii=False 生效
