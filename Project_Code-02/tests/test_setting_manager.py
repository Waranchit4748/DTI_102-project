import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core import settings_manager


@pytest.fixture
def temp_config(monkeypatch, tmp_path):
    fake_config = tmp_path / "config.json"
    monkeypatch.setattr(settings_manager, "CONFIG_FILE", fake_config)
    return fake_config


def test_load_config_defaults(temp_config):
    if temp_config.exists():
        temp_config.unlink()
    cfg = settings_manager.load_config()
    assert cfg == settings_manager.DEFAULT_CONFIG


def test_save_and_load_roundtrip(temp_config):
    data = settings_manager.DEFAULT_CONFIG.copy()
    data["theme"] = "light"
    assert settings_manager.save_config(data)
    loaded = settings_manager.load_config()
    assert loaded["theme"] == "light"


def test_get_and_set_setting(temp_config):
    settings_manager.set_setting("theme", "light")
    value = settings_manager.get_setting("theme")
    assert value == "light"


def test_reset_config(temp_config):
    settings_manager.set_theme("light")
    assert settings_manager.get_theme() == "light"
    settings_manager.reset_config()
    value = settings_manager.get_theme()
    assert value == "dark"


def test_corrupted_file_handling(temp_config):
    temp_config.parent.mkdir(exist_ok=True)
    with open(temp_config, "w", encoding="utf-8") as f:
        f.write("invalid json")

    cfg = settings_manager.load_config()
    assert cfg == settings_manager.DEFAULT_CONFIG

def test_convenience_functions(temp_config):
    assert settings_manager.set_theme("light")
    assert settings_manager.get_theme() == "light"
    assert settings_manager.set_theme("invalid") == False

    settings_manager.set_volume(0.8)
    assert settings_manager.get_volume() == 0.8


def test_volume_clamping(temp_config):

    settings_manager.set_volume(1.5)
    assert settings_manager.get_volume() == 1.0

    settings_manager.set_volume(-0.5)
    assert settings_manager.get_volume() == 0.0