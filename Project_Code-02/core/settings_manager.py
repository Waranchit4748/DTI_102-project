import json
from pathlib import Path
from typing import Any, Dict, Optional
import shutil

CONFIG_DIR = Path("config")
CONFIG_FILE = CONFIG_DIR / "config.json"
BACKUP_FILE = CONFIG_DIR / "config.backup.json"

DEFAULT_CONFIG = {
    "game": {
        "time_limit": 180,
        "max_guesses": 50,
        "starting_difficulty": "easy"
    },
    "display": {
        "theme": "dark",
        "show_hints": True
    },
    "audio": {
        "sound_enabled": True,
        "volume": 0.7
    },
    "language": "th"
}

def _ensure_config_file() -> None:
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG)

def _merge_configs(default: Dict[str, Any], custom: Dict[str, Any]) -> Dict[str, Any]:
    result = default.copy()
    for key, value in custom.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge_configs(result[key], value)
        else:
            result[key] = value
    return result

def _get_nested_value(config: Dict[str, Any], key_path: str, default: Any = None) -> Any:
    try:
        keys = key_path.split('.')
        value = config
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default

def _set_nested_value(config: Dict[str, Any], key_path: str, value: Any) -> bool:
    try:
        keys = key_path.split('.')
        current = config
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
        return True
    except Exception as e:
        print(f"[Settings ERROR] Failed to set '{key_path}': {e}")
        return False

def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    if config_path is None:
        config_path = CONFIG_FILE
    _ensure_config_file()
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        merged = _merge_configs(DEFAULT_CONFIG, config)
        return merged
    except json.JSONDecodeError as e:
        print(f"[Settings ERROR] Corrupted config file: {e}")
        print("[Settings] Loading default config instead")
        return DEFAULT_CONFIG.copy()
    except Exception as e:
        print(f"[Settings ERROR] Failed to load config: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(cfg_dict: Dict[str, Any], config_path: Optional[Path] = None) -> bool:
    if config_path is None:
        config_path = CONFIG_FILE
    try:
        config_path.parent.mkdir(parents=True, exist_ok=True)
        if config_path.exists():
            try:
                shutil.copy2(config_path, BACKUP_FILE)
            except Exception as e:
                print(f"[Settings WARNING] Could not create backup: {e}")
        temp_file = config_path.with_suffix('.tmp')
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(cfg_dict, f, ensure_ascii=False, indent=2)
        temp_file.replace(config_path)
        print(f"[Settings] Config saved to {config_path}")
        return True
    except Exception as e:
        print(f"[Settings ERROR] Failed to save config: {e}")
        temp_file = config_path.with_suffix('.tmp')
        if temp_file.exists():
            temp_file.unlink()
        return False

def get_setting(key_path: str, default: Any = None) -> Any:
    config = load_config()
    return _get_nested_value(config, key_path, default)


def set_setting(key_path: str, value: Any) -> bool:
    config = load_config()
    if _set_nested_value(config, key_path, value):
        return save_config(config)
    return False

def reset_config() -> bool:
    print("[Settings] Resetting config to defaults...")
    return save_config(DEFAULT_CONFIG.copy())

def get_theme() -> str:
    return get_setting("display.theme", "dark")

def set_theme(theme: str) -> bool:
    if theme not in ["dark", "light"]:
        print(f"[Settings WARNING] Invalid theme: {theme}")
        return False
    return set_setting("display.theme", theme)

def get_volume() -> float:
    return get_setting("audio.music_volume", 0.5)

def set_volume(volume: float) -> bool:
    volume = max(0.0, min(1.0, volume))
    return set_setting("audio.music_volume", volume)

def _get_nested(config, key_path, default=None):
    try:
        keys = key_path.split('.')
        value = config
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default

def get_setting(key, default=None):
    config = load_config()
    if '.' in key:
        return _get_nested(config, key, default)
    return config.get(key, default)