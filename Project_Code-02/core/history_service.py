import json #อ่านไฟล์
import shutil #จัดการไฟล์
from datetime import datetime #นำเข้าคลาส จัดรูปแบบเวลา
 
HISTORY_FILE = "data/game_history.json" #เก็บไฟล์บันทึกการเล่นเกม
 
#บันทึกประวัติเกมลงไฟล์ history
def save_history(new_game): #อ่านประวัติเกมเดิม และเพิ่มประวัติเกมใหม่
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f: #เปิดไฟล์โหมดอ่าน รองรับตัวอักษรหลายภาษา
            history = json.load(f)
    except FileNotFoundError: #ถ้าไม่มีไฟล์
        history = [] #เริ่มเป็นลิสต์ว่าง
 
    history.append(new_game) #เพิ่มเกมใหม่เข้ามาในลิสต์
 
    with open(HISTORY_FILE, "w", encoding="utf-8") as f: #เปิดไฟล์โหมดเขียน โดยจะเขียนทับไฟล์เดิม และสร้างไฟล์ใหม่ถ้าไม่มี
        json.dump(history, f, ensure_ascii=False, indent=2)
        #เขียนลงไฟล์เป็น json   เก็บข้อความเป็นตัวอักษรจริง จัดรูปแบบ 2 ช่องว่างเพื่อให้อ่านง่าย
#โหลดประวัติการเล่น
def load_history(limit=10): #ค่าเริ่มต้น10 เนื่องจากจะแสดงประประวัติการเล่น
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f: #เปิดไฟล์โหมดอ่าน รองรับตัวอักษรหลายภาษา
            history = json.load(f) 
 
        # จำกัดจำนวน
        if limit and limit > 0:
            history = history[-limit:] #เอารายการล่าสุดจาก list
        return history #ถ้าhistory มีรายการน้อยกว่า limit จะคืนค่าhistoryทั้งหมด
    except: #ตรวจสอบข้อผิดพลาด
        return [] #คืนลิสต์ว่าง
 
 
def get_recent(n = 10):
    history = load_history() #เรียกฟังก์ชัน
    return history[-n:] if len(history) > n else history
    #คืนค่า n รายการล่าสุด ถ้าhistory มากกว่า n ถ้าน้อยกว่า จะคืนทั้งหมด
#เคลียร์ประวัติการเล่น
def clear_history():
    try:
        # สำรองข้อมูล
        backup_name = f"game_history_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json" #ชื่อไฟล์
        shutil.copy(HISTORY_FILE, backup_name) #คัดลอกไฟล์จากHISTORY_FILEเป็นชื่อไฟล์ใหม่backup_name
        print(f"สำรองข้อมูลไว้ที่: {backup_name}")
 
        # ลบข้อมูล
        with open(HISTORY_FILE, "w", encoding="utf-8") as f: #เปิดไฟล์โหมดเขียน โดยจะเขียนทับไฟล์เดิม และสร้างไฟล์ใหม่ถ้าไม่มี
            json.dump([], f) #เขียนไฟล์json []
        print("ลบประวัติแล้ว")
        return True #คืนค่าTrueเพื่อแสดงว่าสำเร็จแล้ว
    except Exception as e: #ตรวจสอบข้อผิดพลาด เชื่อมกับตัวแปรe
        print(f"ผิดพลาด: {e}") #แสดงข้อความผิดพลาด เพื่อช่วยdebugging
        return False #คืนค่าTrueเพื่อแสดงว่าไม่สำเร็จ
 
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
    total_games = len(all_games) #นับจำนวนเกมทั้งหมด
    total_wins = 0
    total_guesses = 0
    total_hints = 0
    total_similarity = 0
    total_duration = 0
    #เป็น0เพื่อใช้ในการบวกค่า
    #เช็ค แพ้/ชนะ
    for game in all_games:
        if game.get("result") == "win": #ใช้getเพื่อป้องกัน key error ถ้า key ไม่อยู่จะคืนค่า none
            total_wins += 1 #นับจำนวนเกมที่ผู้เล่นชนะ
 
        total_guesses += len(game.get("guesses", [])) #จำนวนครั้งในการทาย
        total_hints += game.get("hints_used", 0) #จำนวนคำใบ้ที่ใช้
        total_similarity += game.get("avg_similarity", 0) #ค่าเฉลี่ยความคล้าย
        total_duration += game.get("duration_sec", 0) #เวลาในการเล่นเกม
 
    # คำนวณค่าเฉลี่ยและ win_rate ทศนิยม 2 ตำแหน่ง
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