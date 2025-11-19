import time
import logging
from core.embedding_service import similarity, has_word, get_top_similar, get_category, get_words_by_category, \
    adjusted_similarity
from core.ranking_service import rank_words, get_rank_for_word
from core.difficulty_loader import get_random_target, load_words
from core.history_service import save_history
from core.achievement_service import check_unlock
from core.utils import normalize_text
import random
import json

logger = logging.getLogger(__name__)

#ตัวกำหนดการชนะ
WIN_THRESHOLD = 1.00
MAX_HINTS = 3
TIME_LIMIT = 180  # seconds

game_state = {
    'level': None,
    'target': None,
    'start_ts': None,
    'guesses': [],
    'time_left': TIME_LIMIT,
    'round_id': None,
    'is_active': False,
    'hints_used': 0,
    'all_words': []
}

#หน้าหลักเลือกระดับความยากของเกม e,m,h
def start_game(level):
    global game_state

    if level not in ['easy', 'medium', 'hard']:
        raise ValueError(f"Invalid level: {level}")

    try:
        all_words = load_words(level)
        target = get_random_target(level)
    except Exception as e:
        logger.error(f"Error loading level data: {e}")
        raise

#ตั้งค่าสถานะของเกม
    game_state = {
        'level': level,
        'target': target,
        'start_ts': time.time(),
        'guesses': [],
        'time_left': TIME_LIMIT,
        'round_id': int(time.time() * 1000),
        'is_active': True,
        'hints_used': 0,
        'all_words': all_words
    }
#log ที่แสดงว่า level เกมอยู่ที่ level ไหน target คืออะไรและคำมีทั้งหมดกี่คำ
    logger.info(f"[START] level={level}, target={target}, words={len(all_words)}")

    return {
        "level": level,
        "target_length": len(target),
        "time_limit": TIME_LIMIT
    }

#ตรวจคำที่ผู้เล่นทายเข้ามา
def check_guess(guess):

    global game_state

#เช็กว่าเกมกำลัง active อยู่หรือป่าว
    if not game_state.get('is_active', False):
        return {
            "status": "game_not_active",
            "message": "เกมยังไม่เริ่ม หรือจบไปแล้ว",
            "score": None,
            "is_win": False,
            "rank": None,
            "guess_count": 0
        }

    level = game_state['level']

#เช็กหมดเวลาการเล่น
    elapsed = time.time() - game_state['start_ts']
    if elapsed >= TIME_LIMIT:
        logger.info("[TIMEOUT] Time limit exceeded")
        target = game_state['target']
        category = get_category(level, target)
        end_round("timeout")
        return {
            "status": "timeout",
            "message": "หมดเวลา! เกมจบแล้ว",
            "target": target,
            "category": category,
            "score": None,
            "is_win": False,
            "rank": None,
            "guess_count": len(game_state['guesses'])
        }
#แปลงคำที่ผู้เล่นพิมพ์มา
    guess_normalized = normalize_text(guess)

#ตรวจสอบคำที่อยู่ในพจนานุกรม
    if not has_word(level, guess_normalized):
        logger.warning(f"[GUESS] Unknown word: {guess_normalized}")
        return {
            "status": "unknown_word",
            "message": f"ไม่มีคำ '{guess}' ในชุดคำศัพท์",
            "score": None,
            "is_win": False,
            "rank": None,
            "guess_count": len(game_state['guesses'])
        }

#ตรวจสอบคำที่เคยถูกเดา
    if any(g['word'] == guess_normalized for g in game_state['guesses']):
        logger.info(f"[GUESS] Already guessed: {guess_normalized}")
        return {
            "status": "already_guessed",
            "message": f"คุณทายคำ '{guess}' ไปแล้ว",
            "score": None,
            "is_win": False,
            "rank": None,
            "guess_count": len(game_state['guesses'])
        }

#หาค่า similarity/score
    try:
        target = game_state['target']

        score = adjusted_similarity(level, guess_normalized, target)
        if score is None:
            raise ValueError("Similarity returned None")
    except Exception as e:
        logger.error(f"[ERROR] similarity(): {e}")
        return {
            "status": "error",
            "message": "เกิดข้อผิดพลาดในการคำนวณ",
            "score": None,
            "is_win": False,
            "rank": None,
            "guess_count": len(game_state['guesses'])
        }

#จัดอันดับคำทั้งหมดเทียบกับ target ผ่าน rank_words
    try:
        all_words = game_state['all_words']
        ranked_list = rank_words(level, target, all_words, top_n=len(all_words))
        rank = get_rank_for_word(guess_normalized, ranked_list) or len(all_words)
    except Exception as e:
        logger.error(f"[ERROR] ranking(): {e}")
        rank = None

#คำนวณเวลาที่ทาย(วินาทีที่ผ่านไปจากเริ่มรอบ)
    elapsed_time = int(time.time() - game_state['start_ts'])
    game_state['guesses'].append({
        "word": guess_normalized,
        "score": score,
        "rank": rank,
        "time": elapsed_time
    })
#สรุปการเดา
    logger.info(f"[GUESS] {guess_normalized} → score={score:.3f}, rank={rank}")

#ตรวจสอบว่าคะแนนถึง1.0 หรือป่าว
    is_win = score == WIN_THRESHOLD
    if is_win:
        logger.info(f"[WIN] Player guessed target '{target}'")
        end_round("win")

        try:
            with open("data/game_history.json", "r", encoding="utf-8") as f:
                history = json.load(f)
                summary = history[-1] if history else {}
        except FileNotFoundError:
            summary = {}

        return {
            "status": "ok",
            "score": float(score),
            "is_win": True,
            "rank": rank,
            "message": _get_feedback_message(score, True),
            "guess_count": len(game_state['guesses']),
            "result": summary.get("result"),  # เพิ่มใหม่
            "target": summary.get("target"),  # เพิ่มใหม่
            "target_category": summary.get("target_category"),  # เพิ่มใหม่
            "guesses": summary.get("guesses", []),  # เพิ่มใหม่
            "duration_sec": summary.get("duration_sec", 0),  # เพิ่มใหม่
            "hints_used": summary.get("hints_used", 0),  # เพิ่มใหม่
        }

    else:
        return {
            "status": "ok",
            "score": float(score),
            "is_win": False,
            "rank": rank,
            "message": _get_feedback_message(score, False),
            "guess_count": len(game_state['guesses'])
        }

#ฟังก์ชั่นให้คำใบ้
def get_hint():

    global game_state
#เมื่อเกมยังไม่เริ่มหรือไม่มีคำ target
    if not game_state.get('is_active', False) or not game_state.get('target'):
        return {
            "status": "error",
            "hint": "",
            "hints_used": game_state.get('hints_used', 0),
            "hints_remaining": MAX_HINTS,
            "message": "เกมยังไม่เริ่ม"
        }

#ถ้าใช้คำใบ้ครบตาม Max_hints
    if game_state['hints_used'] >= MAX_HINTS:
        return {
            "status": "limit_reached",
            "hint": "",
            "hints_used": game_state['hints_used'],
            "hints_remaining": 0,
            "message": f"ใช้คำใบ้ครบ {MAX_HINTS} ครั้งแล้ว"
        }

    level = game_state['level']
    target = game_state['target']
    guessed_words = [g['word'] for g in game_state['guesses']]

    try:
        hint_word = ""
        step = game_state['hints_used']

        if step == 0:

    #บอกหมวดหมู่
            category = get_category(level, target)
            hint_word = f"อยู่ในหมวด '{category}'" if category != "unknown" else "หมวดไม่ระบุ"

    #word จาก same category ไม่ซ้ำคำเดิม
        elif step == 1:
            category = get_category(level, target)
            words_by_cat = get_words_by_category(level)
            words_in_cat = words_by_cat.get(category, [])
            candidates = [w for w in words_in_cat if w != target and w not in guessed_words]
            hint_word = random.choice(candidates) if candidates else "ไม่มีคำใบ้เพิ่มเติม"
    #บอกคำที่คล้ายกับคำเป้าหมาย
        else:
            # ขั้นสาม: word จาก top similar
            similar_words = get_top_similar(level, target, n=20)
            candidates = [w for w, _ in similar_words if w not in guessed_words and w != target]
            hint_word = random.choice(candidates) if candidates else "ไม่มีคำใบ้เพิ่มเติม"

    #อัพเดตสถานะคำใบ้
        game_state['hints_used'] += 1
        remaining = MAX_HINTS - game_state['hints_used']

        logger.info(f"[HINT-{step + 1}] {hint_word} ({game_state['hints_used']}/{MAX_HINTS})")

        return {
            "status": "ok",
            "hint": hint_word if step == 0 else f"ลองคำว่า '{hint_word}' ดูสิ",
            "hints_used": game_state['hints_used'],
            "hints_remaining": remaining
        }

    #มีไว้บอก error ของเกม
    except Exception as e:
        logger.error(f"[ERROR] get_hint(): {e}")
        return {
            "status": "error",
            "hint": "ไม่สามารถให้คำใบ้ได้",
            "hints_used": game_state['hints_used'],
            "hints_remaining": MAX_HINTS - game_state['hints_used']
        }

#ฟังก์ชั่นปุ่มยอมแพ้
def give_up():
    logger.info("[GIVE UP]")
    if not game_state.get('is_active', False):
        return {
            "status": "error",
            "message": "เกมไม่ได้เปิดอยู่",
            "target": None,
            "category": None,
            "score": None,
            "is_win": False,
            "rank": None,
            "guess_count": 0
        }

    target = game_state.get('target', '')
    level = game_state.get('level', 'easy')
    category = get_category(level, target) if target else 'unknown'

    summary = end_round("give_up")

    summary.update({
        "status": "give_up",
        "target": target,
        "category": category,
        "message": f"คำตอบคือ '{target}' (หมวด: {category})",
        "guess_count": len(game_state.get('guesses', []))
    })

    return summary

def handle_timeout():
    logger.info("[TIMEOUT]")
    if not game_state.get('is_active', False):
        return {
            "status": "error",
            "message": "เกมไม่ได้เปิดอยู่",
            "target": None,
            "category": None,
            "score": None,
            "is_win": False,
            "rank": None,
            "guess_count": 0
        }
    target = game_state.get('target', '')
    level = game_state.get('level', 'easy')
    category = get_category(level, target) if target else 'unknown'

    summary = end_round("timeout")  # ส่ง "timeout" แทน "give_up"
    summary.update({
        "status": "timeout",
        "target": target,
        "category": category,
        "message": f"หมดเวลา! คำตอบคือ '{target}' (หมวด: {category})",
        "guess_count": len(game_state.get('guesses', []))
    })

    return summary

#จัดการสิ้นสุดรอบเกม
def end_round(result):
    global game_state

    if not game_state.get('is_active', False):
        logger.warning("end_round called when inactive")
        return {}

    game_state['is_active'] = False
    duration_sec = int(time.time() - game_state['start_ts'])
    guesses = game_state['guesses']
    target = game_state['target']
    hints_used = game_state['hints_used']
    level = game_state['level']

#ค่านวณค่า average similarity
    avg_similarity = sum(g['score'] for g in guesses) / len(guesses) if guesses else 0.0

#
    if result == "win" and guesses:
        guess_eff = max(0.0, 1 - len(guesses) / 20)
        time_eff = max(0.0, 1 - duration_sec / TIME_LIMIT)
        hint_penalty = hints_used * 0.1
        efficiency = max(0.0, min(1.0, (guess_eff * 0.5 + time_eff * 0.5) - hint_penalty))
    else:
        efficiency = 0.0

    target_category = get_category(level, target)

    session_data = {
        "ts": int(time.time()),
        "level": game_state['level'],
        "target": target,
        "target_category": target_category,
        "result": result,
        "guesses": guesses,
        "duration_sec": duration_sec,
        "avg_similarity": avg_similarity,
        "efficiency": efficiency,
        "hints_used": hints_used,
    }
#บันทึกประวัติหลังจบเกม,ตรวจรางวัล
    try:
        save_history(session_data)
        unlocked = check_unlock(session_data)
        session_data['unlocked_achievements'] = unlocked
    except Exception as e:
        logger.error(f"[ERROR] post-end-round: {e}")
        session_data['unlocked_achievements'] = []

    logger.info(f"[END] result={result}, guesses={len(guesses)}, hints={hints_used}")
    return session_data


def get_game_state():
    return {
        "is_active": game_state['is_active'],
        "level": game_state['level'],
        "guesses": game_state['guesses'],
        "round": len(game_state['guesses']),
        "hints_used": game_state['hints_used'],
        "time_elapsed": int(time.time() - game_state['start_ts']) if game_state['start_ts'] else 0,
        "time_remaining": max(0,
                              TIME_LIMIT - (int(time.time() - game_state['start_ts']) if game_state['start_ts'] else 0))
    }


def _get_feedback_message(score: float, is_win: bool):
    """สร้างข้อความ feedback ตามคะแนน"""
    if is_win:
        return " ยินดีด้วย! คุณทายถูกแล้ว!"
    elif score >= 0.8:
        return "ใกล้มากๆ! เกือบได้แล้ว!"
    elif score >= 0.7:
        return "ใกล้แล้ว! ทิศทางถูกต้อง!"
    elif score >= 0.5:
        return "ใกล้พอสมควร คิดต่อได้!"
    elif score >= 0.3:
        return "ยังไกลอยู่ ลองเปลี่ยนทิศทาง!"
    else:
        return "ยังไกลมาก ลองคิดใหม่!"