"""core/difficulty_loader.py: โหลดและจัดการระดับความยาก"""

import random
import json
import logging
from pathlib import Path
from core.embedding_service import get_words, get_words_by_category, load_embeddings, embedding_data

logger = logging.getLogger(__name__)

# ไฟล์สำหรับบันทึกประวัติการเล่น
CONFIG_FILE = Path("data/difficulty_config.json")

# ค่าเริ่มต้มของเกม
DEFAULT_CONFIG = {
    "current_level": "easy", # ระดับเริ่มต้น
    "thresholds": {
        "easy_to_medium" : 5, # ถ้าทายได้ภายใน 5 ครั้งแนะนำขึ้น medium
        "medium_to_hard" : 10, # ถ้าทายได้ภายใน 10 ครั้ง แนะนำขึ้น hard
        "hard_to_medium" : 15 # ถ้าทายเกิน 15 ครั้ง → แนะนำลง medium
    }
}

def load_words(level) :
    """โหลดคำศัพท์ทั้งหมดจากระดับที่กำหนด"""
    
    # ตรวจสอบว่ามี embedding data หรือยัง ถ้าไม่มีให้โหลด
    if level not in embedding_data :
        try :
            # ถ้ายังไม่มี ให้โหลด embeddings จากไฟล์
            load_embeddings(level)
        except Exception as e :
            # ถ้าโหลดไม่สำเร็จ (เช่น ไฟล์ไม่มี หรือ format ผิด)
            logger.error (f"Failed to load embeddings for level {level}: {level}")
            raise
    
    # รายการคำศัพท์ที่อยู่ใน level นั้น
    return get_words(level)
    
def load_words_by_category_dict(level) :
    """โหลดคำศัพท์แยกตามหมวดหมู่"""

    # ตรวจสอบและโหลด embeddings ถ้ายังไม่มี
    if level not in embedding_data :
        load_embeddings(level)
    
    # dictionary ที่มี key เป็นหมวดหมู่ และ value เป็นรายการคำ 
    return get_words_by_category(level)

def get_random_target(level):
    """สุ่มคำเป้าหมายจากระดับที่ผู้เล่นเลือก"""
    
    # โหลดคำศัพท์ทั้งหมด
    words = load_words(level)
    # สุ่มเลือกคำหนึ่งคำจากรายการ ไม่มีการป้องกันการสุ่มซ้ำในเกมติดต่อกัน
    return random.choice(words)

def _load_config():
    """โหลด configuration จากไฟล์ หรือใช้ค่า default"""
    
    try :
        # ตรวจสอบว่าไฟล์ difficulty_config.json มีอยู่จริงหรือไม่
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f : # "utf-8" เพื่อรองรับภาษาไทย
                
                config = json.load(f)
                logger.info(f"[Config] Loaded from {CONFIG_FILE}")
                return config
        else :
            # ไฟล์ไม่มีใช้ค่า default (กรณีรันครั้งแรก)
            logger.info(f"[Config] Using default config")
            return DEFAULT_CONFIG
    
    except Exception as e :
        logger.error(f"Failed to load config: {e}, using default config")
        return DEFAULT_CONFIG.copy()
    
def _save_config(config):
    """บันทึก configuration ลงไฟล์"""

    try :
        # สร้าง folder ถ้ายังไม่มี
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        # เปิดไฟล์และเขียน JSON
        with open(CONFIG_FILE, "w", encoding="utf-8") as f :
            json.dump(config, f, indent=2, ensure_ascii=False)
        logger.info(f"[Config] Saved to {CONFIG_FILE}")
    except Exception as e :
        logger.error(f"[Config] Failed to save: {e}")
        
def get_current_level() :
    """ดึงระดับความยากปัจจุบัน"""
    
    # ดึงค่า current_level จาก config
    # ถ้าไม่มี key นี้ ให้ใช้ "easy" เป็น default
    config = _load_config()
    return config.get("current_level", "easy")

def persist_current_level(level) :
    """บันทึกระดับความยากปัจจุบันลง config file"""
    
    # ตรวจสอบว่า level ถูกต้อง
    if level not in ["easy", "medium", "hard"] :
        return
    # โหลด config ปัจจุบัน
    config = _load_config()
    # อัปเดตระดับใหม่
    config["current_level"] = level
    _save_config(config)
    
def get_thresholds() :
    """ดึงค่า threshold สำหรับการปรับระดับอัตโนมัติ"""
    
    config = _load_config()
    # ดึง thresholds จาก config ถ้าไม่มีให้ใช้ค่า default
    return config.get("thresholds", DEFAULT_CONFIG["thresholds"])

def adjust_difficulty(avg_guesses, current_level):
    """แนะนำระดับความยากตามจำนวนครั้งที่ทายเฉลี่ย"""
    
    # โหลดค่า threshold ต่างๆ
    thresholds = get_thresholds()
    
    # ดึงค่า threshold แต่ละตัว พร้อมค่า default ถ้าไม่มี key นั้นใน dict
    easy_up = thresholds.get("easy_to_medium", 5)
    medium_up = thresholds.get("medium_to_hard", 5)
    hard_down = thresholds.get("hard_to_medium", 15)
    medium_down = thresholds.get("medium_to_easy", 15)
    
    # กำลังเล่นในระดับ easy
    if current_level == "easy" :
        # ถ้าทายได้เร็วใน level easy แนะนำขึ้นไป medium
        if avg_guesses <= easy_up :
            logger.info(f"[Auto-adjust] avg_guesses={avg_guesses:.1f} <= {easy_up} → Suggest: medium")
            return "medium"
        else :
            # ถ้าทายช้ากว่า easy_up
            return "easy"
        
    elif current_level == "medium" :
        # ถ้าทายได้เร็วมากใน level medium แนะนำขึ้นไป hard
        if avg_guesses <= medium_up :
            logger.info(f"[auto-adjust] avg_guesses={avg_guesses:.1f} <= {medium_up} -> Suggest: hard")
            return "hard"
        
        # ถ้าทายช้ามากใน level medium แนะนำลงมา easy
        elif avg_guesses >= medium_down :
            logger.info(f"[auto-adjust] avg_guesses={avg_guesses:.1f} >= {medium_down} -> suggest: easy")
            return "easy"
        
        else :
            # ถ้าไม่ถึงเกณฑ์ medium_up และ medium_down อยู่ level medium ต่อ
            return "medium"
    
    elif current_level == "hard" :
        # ถ้าทายช้าใน level hard แนะนำลงมา medium
        if avg_guesses >= hard_down :
           logger.info(f"[Auto-adjust] avg_guesses={avg_guesses:.1f} >= {hard_down} → Suggest: medium") 
           return "medium"
        else :
            # ถ้าทายได้ไว้ อยู่ level hard ต่อ
            return "hard"
        
    # ถ้า current_level ไม่ใช่ easy/medium/hard คืนค่า level ดิม
    return current_level

def analyze_and_suggest(recent_games) :
    """วิเคราะห์เกมล่าสุดและแนะนำระดับความยาก"""
    
    # ดึง level ปัจจุบัน
    current_level = get_current_level()
    
    try :
        from core.history_service import load_history
        
        current_level = get_current_level()
        
        # โหลดประวัติเกม
        sessions = load_history(limit=recent_games)
        # กรองเฉพาะเกมที่เล่นในระดับปัจจุบัน
        level_sessions = [s for s in sessions if s.get("level") == current_level]
        
        # ถ้าไม่มีข้อมูลเพียงพอ
        if not level_sessions :
            return {
                "current_level": current_level,
                "suggested_level": current_level, # แนะนำให้อยู่ระดับเดิม
                "should_change": False, # ไม่ต้องเปลี่ยน
                "reason": "ไม่มีข้อมูลเพียงพอ",
                "avg_guesses": None
            }
        
        # คำนวณจำนวนครั้งที่ทายเฉลี่ย
        avg_guesses = sum(len(s.get("guesses", [])) for s in level_sessions) / len(level_sessions)
        
        # แนะนำระดับใหม่
        suggested_level = adjust_difficulty(avg_guesses, current_level)
        # ตรวจสอบว่าระดับที่แนะนำต่างจากปัจจุบันหรือไม่
        should_change = suggested_level != current_level
        
        # สร้างข้อความแนะนำ
        if should_change :
            if suggested_level > current_level :
                # กรณีแนะนำให้ขึ้น level ถัดไป
                reason = f"คุณทายได้ภายใน {avg_guesses:.1f} ครั้ง (เก่งมาก!) ลองระดับสูงขึ้นไหม?"
            
            else :
                # กรณีแนะนำให้ลด level (ยากไป)
                reason = f"คุณใช้เวลาทาย {avg_guesses:.1f} ครั้ง (ยากไปหน่อย) ลองระดับต่ำกว่าไหม?"
        
        else :
            # level ปัจจุบันเหมาะสมแล้ว
            reason = f"ระดับปัจจุบันเหมาะสม (เฉลี่ย {avg_guesses:.1f} ครั้ง)"
            
        return {
            "current_level": current_level,
            "suggested_level": suggested_level,
            "should_change": should_change,
            "reason": reason,
            "avg_guesses": round(avg_guesses, 1)
        }
    
    except Exception as e :
        logger.error(f"[Auto-adjust] Error: {e}")
        current_level = get_current_level()
        return {
            "current_level": current_level,
            "suggested_level": current_level,
            "should_change": False,
            "reason": "เกิดข้อผิดพลาดในการวิเคราะห์",
            "avg_guesses": None
        }
    
def auto_adjust_for_next_game(recent_games):
    """ปรับระดับความยากอัตโนมัติสำหรับเกมถัดไป"""
    
    # วิเคราะห์และดูว่าควรเปลี่ยน level หรือไม่
    suggestion = analyze_and_suggest(recent_games)
    
    # ดึงข้อมูลที่สำคัญจากผลการวิเคราะห์
    old_level = suggestion["current_level"] 
    new_level = suggestion["suggested_level"]
    change = suggestion["should_change"]
    
    # ถ้าควรเปลี่ยนบันทึก level ใหม่
    if change :
        persist_current_level(new_level)
        logger.info(f"[Auto-change] {old_level} → {new_level} (avg_guesses={suggestion['avg_guesses']})")
    
    # คืนข้อมูลการเปลี่ยนแปลง    
    return {
        "changed": change,
        "old_level": old_level,
        "new_level": new_level,
        "reason": suggestion['reason'],
        "avg_guesses": suggestion['avg_guesses']
    }
    
def should_show_level_change_notification(recent_games) :
    """ตรวจสอบว่าควรแสดง notification แนะนำให้เปลี่ยนระดับไหม"""
    
    # # วิเคราะห์และดึงค่า should_change
    suggestion = analyze_and_suggest(recent_games)
    # คืนค่า True/False ตามผล
    return suggestion["should_change"]