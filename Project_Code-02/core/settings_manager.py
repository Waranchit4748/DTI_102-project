import json
from pathlib import Path

CONFIG_FILE = Path("config/config.json")

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
        "volume": 0.5
    },
    "language": "th"
}
def load_config():
    CONFIG_FILE.parent.mkdir(exist_ok=True)
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return DEFAULT_CONFIG.copy()

#บันทึก config
def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

#การตั้งค่าธีม dark/light
def get_theme():
    config = load_config()
    return config.get("display", {}).get("theme", "dark")

#การคืนค่าธีม
def set_theme(theme):
    config = load_config()
    if "display" not in config:
        config["display"] = {}
    config["display"]["theme"] = theme
    save_config(config)

#การตั้งค่าเสียง
def get_volume():
    config = load_config()
    return config.get("audio", {}).get("volume", 0.5)

#การคืนค่าเสียง
def set_volume(volume):
    volume = max(0.0, min(1.0, float(volume)))  #กำหนด 0.0-1.0
    config = load_config()
    if "audio" not in config:
        config["audio"] = {}
    config["audio"]["volume"] = volume
    save_config(config)

#อ่านค่า config
def get_setting(name, default=None):
    config = load_config()
    return config.get(name, default)

#เปลี่ยนค่า config
def set_setting(name, value):
    config = load_config()
    config[name] = value
    save_config(config)

#รีเซ็ตค่า config เป็นค่า default
def reset_config():
    save_config(DEFAULT_CONFIG.copy())