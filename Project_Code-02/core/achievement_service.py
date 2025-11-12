import json
from pathlib import Path

ACHIEVEMENT_FILE = Path("data/achievements.json")

# Achievement ทั้งหมดที่มีในระบบ
ACHIEVEMENT_DEFINITIONS = {
    "first_win": {
        "name": "ชัยชนะครั้งแรก",
        "description": "ชนะเกมครั้งแรก",
    },
    "perfect_guess": {
        "name": "ทายถูกครั้งเดียว",
        "description": "ชนะด้วยการทายเพียง 1 ครั้ง",
    },
    "speed_demon": {
        "name": "สายฟ้าแลบ",
        "description": "ชนะภายใน 60 วินาที",
    },
    "persistent_player": {
        "name": "นักเล่นถาวร",
        "description": "เล่นครบ 10 รอบ",
    },
    "win_streak_5": {
        "name": "ผู้ชนะต่อเนื่อง",
        "description": "ชนะติดต่อกัน 5 ครั้ง",
    },
    "efficiency_master": {
        "name": "ยอดฝีมือประสิทธิภาพ",
        "description": "Efficiency มากกว่า 80%",
    },
    "hard_mode_champion": {
        "name": "แชมป์โหมดยาก",
        "description": "ชนะในโหมดยาก 5 ครั้ง",
    },
    "hint_free": {
        "name": "ไม่ใช้คำใบ้เลย",
        "description": "ชนะโดยไม่ใช้ hint",
    },
    "no_hint_master": {
        "name": "ปรมาจารย์ไม่ใช้คำใบ้",
        "description": "ชนะโดยไม่ใช้ hint ทุกครั้งที่เล่น",
    },
    "minimal_hints": {
        "name": "คำใบ้น้อยสุด",
        "description": "ชนะโดยใช้ hint ไม่เกิน 1 ครั้ง",
    },
}

# ตัวแปรเก็บสถานะ achievements ที่ปลดล็อกแล้ว
achievements_state = {}


# สร้างสถานะเริ่มต้น
def _create_initial_achievements():

    return {
        "unlocked": [],
        "stats": {
            "total_games": 0,
            "win_streak": 0,
            "hard_mode_wins": 0,
            "no_hint_total": 0,
        }
    }

# โหลดสถานะจากไฟล์
def load_achievements():
    global achievements_state
    if not ACHIEVEMENT_FILE.exists():
        # สร้างโฟลเดอร์ data ก่อน ถ้ายังไม่มี
        ACHIEVEMENT_FILE.parent.mkdir(parents=True, exist_ok=True)
        achievements_state = _create_initial_achievements()
        _save_achievements()
    else:
        with open(ACHIEVEMENT_FILE, "r", encoding="utf-8") as f:
            achievements_state = json.load(f)
    return achievements_state

# บันทึกสถานะลงไฟล์ JSON
def _save_achievements():
    # สร้างโฟลเดอร์ด้วยเผื่อกรณีเรียกจากอื่น
    ACHIEVEMENT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(ACHIEVEMENT_FILE, "w", encoding="utf-8") as f:
        json.dump(achievements_state, f, ensure_ascii=False, indent=2)

# อัปเดตสถิติหลังเล่นเกมจบ 1 รอบ
def _update_statistics(game_data):
    stats = achievements_state["stats"]

    stats["total_games"] += 1

    # ชนะ = เพิ่ม streak
    if game_data.get("result") == "win":
        stats["win_streak"] += 1
        if game_data.get("level") == "hard":
            stats["hard_mode_wins"] += 1
    else:
        stats["win_streak"] = 0  # ถ้าแพ้รีเซ็ต streak

    # ถ้าไม่ใช้ hint ให้เพิ่ม counter
    if game_data.get("hints_used", 0) == 0:
        stats["no_hint_total"] += 1

    _save_achievements()

# ฟังก์ชันปลดล็อก Achievement
def unlock(achievement_id):
    if achievement_id not in achievements_state["unlocked"]:
        achievements_state["unlocked"].append(achievement_id)
        _save_achievements()
        return True
    return False

# ตรวจสอบว่าการเล่นรอบนี้ปลดล็อก Achievement อะไรบ้าง
def check_unlock(game_data):
    _update_statistics(game_data)
    stats = achievements_state["stats"]
    newly_unlocked = []

    # ชนะครั้งแรก
    if game_data.get("result") == "win":
        if "first_win" not in achievements_state["unlocked"]:
            newly_unlocked.append("first_win")

    # ทายถูกครั้งเดียว
    if game_data.get("result") == "win" and game_data.get("guesses") == 1:
        newly_unlocked.append("perfect_guess")

    # ชนะภายใน 60 วิ
    if game_data.get("result") == "win" and game_data.get("duration_sec", 999) <= 60:
        newly_unlocked.append("speed_demon")

    # เล่นครบ 10 รอบ
    if stats["total_games"] >= 10:
        newly_unlocked.append("persistent_player")

    # ชนะติดกัน 5 รอบ
    if stats["win_streak"] >= 5:
        newly_unlocked.append("win_streak_5")

    # efficiency >= 0.8
    if game_data.get("efficiency", 0) >= 0.8:
        newly_unlocked.append("efficiency_master")

    # ชนะในโหมดยาก 5 ครั้ง
    if stats["hard_mode_wins"] >= 5:
        newly_unlocked.append("hard_mode_champion")

    # ชนะโดยไม่ใช้ hint
    if game_data.get("result") == "win" and game_data.get("hints_used", 99) == 0:
        newly_unlocked.append("hint_free")

    # เล่นทั้งหมดโดยไม่เคยใช้ hint เลย
    if stats["no_hint_total"] >= stats["total_games"] > 0:
        newly_unlocked.append("no_hint_master")

    # ชนะโดยใช้ hint ไม่เกิน 1 ครั้ง
    if game_data.get("result") == "win" and game_data.get("hints_used", 99) <= 1:
        newly_unlocked.append("minimal_hints")

    # บันทึกลง unlocked list ถ้ายังไม่มี
    for a in newly_unlocked:
        if a not in achievements_state["unlocked"]:
            achievements_state["unlocked"].append(a)

    if newly_unlocked:
        _save_achievements()
    return newly_unlocked

# ฟังก์ชันอ่านข้อมูล
def get_unlocked():
    return achievements_state.get("unlocked", []) #คืนค่ารายชื่อ Achievement ที่ปลดล็อกแล้วทั้งหมด