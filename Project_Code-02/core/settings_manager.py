import json
from pathlib import Path
import copy
import vlc # ใช้สำหรับเล่นเพลงจาก URL

CONFIG_FILE = Path("config/config.json")

# ค่าเริ่มต้น config
DEFAULT_CONFIG = {
    "theme": "dark",
    "sound_enabled": True,
    "volume": 0.7,
    "current_level": "easy",
    "timer_duration": 180,
    "show_hints": True,
    "language": "th",
    "background_music": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-6.mp3"
}

# สร้างไฟล์ config ถ้าไม่มี
def _ensure_config_file():
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE.exists():
        save_config(DEFAULT_CONFIG.copy())

# โหลดไฟล์ config 
def load_config(config_file=CONFIG_FILE):
    if not config_file.exists():
        save_config(DEFAULT_CONFIG.copy(), config_file)
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        cfg = copy.deepcopy(DEFAULT_CONFIG)
        cfg.update(data)
        return cfg
    except:
        save_config(DEFAULT_CONFIG.copy(), config_file)
        return copy.deepcopy(DEFAULT_CONFIG)

# บันทึกไฟล์ config
def save_config(cfg_dict, config_file=CONFIG_FILE):
    config_file.parent.mkdir(parents=True, exist_ok=True)
    temp_file = config_file.with_suffix(".tmp")
    with open(temp_file, "w", encoding="utf-8") as f:
        json.dump(cfg_dict, f, ensure_ascii=False, indent=2)
    temp_file.replace(config_file)
    return True

# อ่านค่าการตั้งค่า
def get_setting(key, default=None):
    cfg = load_config()
    return cfg.get(key, default)

# เปลี่ยนค่าการตั้งค่า
def set_setting(key, value):
    cfg = load_config()
    cfg[key] = value
    save_config(cfg)
    return True

# รีเซ็ตค่า config เป็นค่าเริ่มต้น
def reset_config():
    save_config(copy.deepcopy(DEFAULT_CONFIG))
    return True

# ฟังก์ชันเปลี่ยนการตั้งค่าและกำหนดค่่าธีม
def get_theme():
    return get_setting("theme", "dark")

def set_theme(theme):
    if theme not in ["dark", "light"]:
        print("Theme ต้องเป็น dark หรือ light")
        return False
    return set_setting("theme", theme)

# ฟังก์ชันเปลี่ยนการตั้งค่าและกำหนดค่่าเสียง
def get_volume():
    return get_setting("volume", 0.7)

def set_volume(vol):
    vol = max(0.0, min(1.0, float(vol)))
    return set_setting("volume", vol)

# ฟังก์ชันเปลี่ยนการตั้งค่าและกำหนดค่่าเพลง
def is_sound_enabled():
    return get_setting("sound_enabled", True)

# คืนค่า URL เพลงประกอบ
def get_music_url():
    return get_setting("background_music")

# เปลี่ยนเพลงประกอบ
def set_music_url(url):
    return set_setting("background_music", url)

# สลับเปิด/ปิดเสียง
def toggle_sound():
    current = is_sound_enabled()
    return set_setting("sound_enabled", not current)

# เล่นเพลงจาก URL ด้วย VLC
_music_player = None # เก็บ instance ของ vlc.MediaPlayer

def play_music():
    global _music_player
    if not is_sound_enabled():
        print("เสียงปิดอยู่ ไม่เล่นเพลง")
        return
    url = get_music_url()
    try:
        _music_player = vlc.MediaPlayer(url) # สร้าง player
        _music_player.audio_set_volume(int(get_volume() * 100)) # VLC ใช้ 0-100
        result = _music_player.play()
        if result == -1: # -1 หมายถึง VLC เล่นไม่ได้
            print("ไม่สามารถเล่นเพลงได้: ตรวจสอบ URL หรือ VLC ติดตั้งอยู่หรือไม่")
        else:
            print(f"🎵 เล่นเพลงจาก URL: {url}")
    except Exception as e:
        print("ไม่สามารถเล่นเพลงได้:", e)

# หยุดเพลงและคืน resource ของ player
def stop_music():
    global _music_player
    if _music_player:
        _music_player.stop()
        _music_player.release()
        _music_player = None

if __name__ == "__main__":
    reset_config()
    print(f"✅ Config file ready at: {CONFIG_FILE.resolve()}")
    play_music()
    input("กด Enter เพื่อหยุดเพลงและออก...")
    stop_music()