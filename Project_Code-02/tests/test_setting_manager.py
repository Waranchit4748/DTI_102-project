import sys, os
from pathlib import Path
import shutil
import json
import tempfile

# เพิ่ม path ของ project
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.settings_manager import (
    load_config, save_config,
    get_theme, set_theme,
    get_volume, set_volume,
    get_setting, set_setting,
    reset_config, CONFIG_FILE
)

# สร้างไฟล์ config ชั่วคราวสำหรับทดสอบ
TEST_CONFIG_DIR = Path(tempfile.gettempdir()) / "test_config"
TEST_CONFIG_FILE = TEST_CONFIG_DIR / "config.json"

def use_test_config_file():
    global CONFIG_FILE
    CONFIG_FILE = TEST_CONFIG_FILE
    TEST_CONFIG_DIR.mkdir(exist_ok=True)

# ฟังก์ชันช่วยสำหรับแสดงผล
def print_result(name, passed):
    print(f"{name}: {'✅ Passed' if passed else '❌ Failed'}")

# -------------------------------
# 1. Test load_config() → default ถ้าไม่มีไฟล์
# -------------------------------
def test_load_default():
    use_test_config_file()
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
    config = load_config()
    expected = {
        "game": {"time_limit": 180, "max_guesses": 50, "starting_difficulty": "easy"},
        "display": {"theme": "dark", "show_hints": True},
        "audio": {"sound_enabled": True, "volume": 0.7},
        "language": "th"
    }
    print_result("Test load_config() default", config == expected)

# -------------------------------
# 2. Test save_config() + load_config()
# -------------------------------
def test_save_and_load():
    use_test_config_file()
    test_config = {
        "game": {"time_limit": 100, "max_guesses": 10, "starting_difficulty": "medium"},
        "display": {"theme": "light", "show_hints": False},
        "audio": {"sound_enabled": False, "volume": 0.3},
        "language": "en"
    }
    save_config(test_config)
    loaded = load_config()
    print_result("Test save_config() + load_config()", loaded == test_config)

# -------------------------------
# 3. Test theme functions
# -------------------------------
def test_theme():
    use_test_config_file()
    set_theme("light")
    print_result("Set theme light", get_theme() == "light")

    set_theme("dark")
    print_result("Set theme dark", get_theme() == "dark")

# -------------------------------
# 4. Test volume functions
# -------------------------------
def test_volume():
    use_test_config_file()
    set_volume(0.5)
    print_result("Set volume 0.5", get_volume() == 0.5)

    set_volume(1.5)
    print_result("Set volume >1 capped", get_volume() == 1.0)

    set_volume(-0.2)
    print_result("Set volume <0 capped", get_volume() == 0.0)

# -------------------------------
# 5. Test get_setting() / set_setting()
# -------------------------------
def test_get_set_setting():
    use_test_config_file()
    set_setting("language", "jp")
    lang = get_setting("language")
    print_result("get_setting / set_setting", lang == "jp")

    set_setting("custom_key", 123)
    val = get_setting("custom_key")
    print_result("set_setting custom key", val == 123)

# -------------------------------
# 6. Test reset_config()
# -------------------------------
def test_reset():
    use_test_config_file()
    set_theme("light")
    set_volume(0.2)
    set_setting("language", "kr")
    reset_config()
    print_result("Reset theme", get_theme() == "dark")
    print_result("Reset volume", get_volume() == 0.7)
    print_result("Reset language", get_setting("language") == "th")

# -------------------------------
# 7. Test corrupted file handling
# -------------------------------
def test_corrupted_file():
    use_test_config_file()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write("{ not: valid json }")  # สร้างไฟล์เสีย
    config = load_config()
    # ต้อง fallback ไปค่า default
    print_result("Corrupted file fallback", config.get("language") == "th")

# -------------------------------
# Run all tests
# -------------------------------
if __name__ == "__main__":
    test_load_default()
    test_save_and_load()
    test_theme()
    test_volume()
    test_get_set_setting()
    test_reset()
    test_corrupted_file()

    # ลบไฟล์ทดสอบเมื่อจบ
    if TEST_CONFIG_FILE.exists():
        TEST_CONFIG_FILE.unlink()
    if TEST_CONFIG_DIR.exists():
        TEST_CONFIG_DIR.rmdir()
