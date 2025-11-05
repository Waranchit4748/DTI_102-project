import json
import os
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.history_service import save_history, load_history, clear_history, calc_stats, HISTORY_FILE

# ฟังก์ชันช่วย
def print_result(name, passed):
    print(f"{name}: {'✅ Passed' if passed else '❌ Failed'}")
    
# -------------------------------
# 1. ทดสอบ save_history()
# -------------------------------
def test_save_history():
    # เตรียมไฟล์ว่าง
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)

    # สร้างข้อมูลตัวอย่าง
    sample_game = {
        "result": "win",
        "guesses": ["apple", "grape"],
        "hints_used": 1,
        "avg_similarity": 0.9,
        "duration_sec": 45
    }

    # เพิ่มเกมลงในไฟล์
    save_history(sample_game)

    # ตรวจว่าไฟล์ถูกสร้างและมีข้อมูลถูกต้อง
    if not os.path.exists(HISTORY_FILE):
        print_result("Test save_history() → file created", False)
        return
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    print_result("Test save_history() → file created", True)
    print_result("Test save_history() → correct data", data and data[0]["result"] == "win")

# -------------------------------
# 2. ทดสอบการบันทึกหลายครั้ง
# -------------------------------
def test_multiple_saves():
    # ล้างไฟล์ก่อน
    clear_history()
    g1 = {"result": "win", "guesses": ["cat"], "hints_used": 0}
    g2 = {"result": "lose", "guesses": ["dog"], "hints_used": 2}
    save_history(g1)
    save_history(g2)
    data = load_history()
    print_result("Test multiple saves → appended correctly", len(data) == 2)

# -------------------------------
# 3. ทดสอบพารามิเตอร์ limit
# -------------------------------
def test_limit_parameter():
    data = load_history(limit=1)
    print_result("Test limit parameter", len(data) == 1)

# -------------------------------
# 4. ทดสอบ calc_stats() กับ mock history
# -------------------------------
def test_calc_stats():
    # เขียน mock data ลงไฟล์
    mock = [
        {"result": "win", "guesses": ["a", "b"], "hints_used": 1, "avg_similarity": 0.8, "duration_sec": 50},
        {"result": "lose", "guesses": ["x", "y", "z"], "hints_used": 2, "avg_similarity": 0.6, "duration_sec": 70}
    ]
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(mock, f)

    stats = calc_stats()
    passed = (
        stats["total_games"] == 2 and
        stats["total_wins"] == 1 and
        round(stats["win_rate"], 2) == 0.5
    )
    print_result("Test calc_stats() with mock history", passed)

# -------------------------------
# 5. ทดสอบกรณีไม่มีประวัติ
# -------------------------------
def test_empty_history():
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)
    stats = calc_stats()
    passed = stats["total_games"] == 0
    print_result("Test empty history", passed)

# -------------------------------
# Run all tests
# -------------------------------
if __name__ == "__main__":
    test_save_history()
    test_multiple_saves()
    test_limit_parameter()
    test_calc_stats()
    test_empty_history()
