import json
import shutil
from datetime import datetime
 
HISTORY_FILE = "data/game_history.json"
 
#บันทึกประวัติเกมลงไฟล์ history
def save_history(new_game):
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
    except FileNotFoundError:
        history = []
 
    history.append(new_game)
 
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
 
#โหลดประวัติการเล่น
def load_history(limit=10):
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            history = json.load(f)
 
        # จำกัดจำนวน
        if limit and limit > 0:
            history = history[-limit:]
        return history
    except:
        return []
 
 
def get_recent(n = 10):
    history = load_history()
    return history[-n:] if len(history) > n else history
 
#เคลียร์ประวัติการเล่น
def clear_history():
    try:
        # สำรองข้อมูล
        backup_name = f"game_history_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        shutil.copy(HISTORY_FILE, backup_name) #สำรองไฟล์เดิม
        print(f"สำรองข้อมูลไว้ที่: {backup_name}")
 
        # ลบข้อมูล
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
        print("ลบประวัติแล้ว")
        return True
    except Exception as e:
        print(f"ผิดพลาด: {e}")
        return False
 
#คำนวณสถิติ
def calc_stats():
    all_games = load_history()
    #ยังไม่มีการเล่นเกม
    if not all_games:
        return {
            "total_games": 0,
            "total_wins": 0,
            "win_rate": 0,
            "avg_guesses": 0,
            "avg_hints_used": 0,
            "avg_similarity": 0,
            "avg_duration": 0,
            "per_level": {}
        }
 
    # นับพื้นฐาน
    total_games = len(all_games)
    total_wins = 0
    total_guesses = 0
    total_hints = 0
    total_similarity = 0
    total_duration = 0
 
    #เช็ค แพ้/ชนะ
    for game in all_games:
        if game.get("result") == "win":
            total_wins += 1
 
        total_guesses += len(game.get("guesses", [])) #จำนวนครั้งในการทาย
        total_hints += game.get("hints_used", 0) #จำนวนคำใบ้ที่ใช้
        total_similarity += game.get("avg_similarity", 0) #ค่าเฉลี่ยความคล้าย
        total_duration += game.get("duration_sec", 0) #เวลาในการเล่นเกม
 
    # คำนวณค่าเฉลี่ยและ win_rate
    win_rate = round(total_wins / total_games, 2) if total_games > 0 else 0
    avg_guesses = round(total_guesses / total_games, 2) if total_games > 0 else 0
    avg_hints_used = round(total_hints / total_games, 2) if total_games > 0 else 0
    avg_similarity = round(total_similarity / total_games, 2) if total_games > 0 else 0
    avg_duration = round(total_duration / total_games, 2) if total_games > 0 else 0
 
    return {
        "total_games": total_games,
        "total_wins": total_wins,
        "win_rate": win_rate,
        "avg_guesses": avg_guesses,
        "avg_hints_used": avg_hints_used,
        "avg_similarity": avg_similarity,
        "avg_duration": avg_duration,
        "per_level": {} #ยังไม่ได้ implement แต่เตรียมไว้สำหรับสถิติแยกระดับเกม
    }