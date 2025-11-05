"""
Game Manager Module
จัดการ state ของเกม และ game loop หลัก
"""

import logging
import random
from typing import Optional, Dict, List, Tuple

logger = logging.getLogger(__name__)

# Module-level game state dict
_game_state = {
    "active": False,
    "level": None,
    "target_word": None,
    "guesses": [],
    "round": 0,
    "max_rounds": 6,
    "score": 0,
    "game_over": False,
    "won": False
}


def start_game(level: str = "easy", max_rounds: int = 6) -> Dict:
    """
    เริ่มเกมใหม่ - Mock (return dummy data)
    """
    global _game_state

    # Mock target words
    mock_targets = {
        "easy": ["สุนัข", "แมว", "น้ำ"],
        "medium": ["คอมพิวเตอร์", "โทรศัพท์"],
        "hard": ["ประชาธิปไตย", "วิทยาศาสตร์"]
    }

    target_word = random.choice(mock_targets.get(level, mock_targets["easy"]))

    _game_state = {
        "active": True,
        "level": level,
        "target_word": target_word,
        "guesses": [],
        "round": 0,
        "max_rounds": max_rounds,
        "score": 0,
        "game_over": False,
        "won": False
    }

    return _game_state.copy()


def check_guess(guess: str) -> Dict:
    """
    ตรวจสอบคำทาย - Mock (return random similarity)
    """
    global _game_state

    if not _game_state["active"] or _game_state["game_over"]:
        return {"valid": False, "message": "Game not active"}

    is_correct = (guess == _game_state["target_word"])

    # Mock similarity
    similarity = 1.0 if is_correct else random.uniform(0.1, 0.9)

    _game_state["round"] += 1
    _game_state["guesses"].append({
        "word": guess,
        "similarity": similarity,
        "round": _game_state["round"]
    })

    if is_correct:
        _game_state["won"] = True
        _game_state["game_over"] = True
    elif _game_state["round"] >= _game_state["max_rounds"]:
        _game_state["game_over"] = True

    return {
        "valid": True,
        "similarity": similarity,
        "is_correct": is_correct,
        "round": _game_state["round"]
    }


def get_hint() -> Dict:
    """
    ขอคำใบ้ - Mock (return dummy hint)
    """
    if not _game_state["active"]:
        return {"error": "Game not active"}

    mock_hints = [
        "คำนี้เกี่ยวข้องกับสัตว์",
        "คำนี้มี 2 พยางค์",
        f"อักษรแรกคือ '{_game_state['target_word'][0]}'"
    ]

    hint = random.choice(mock_hints)

    return {"hint": hint, "cost": 10}


def give_up() -> Dict:
    """
    ยอมแพ้ - Mock
    """
    global _game_state

    if not _game_state["active"]:
        return {"error": "Game not active"}

    _game_state["game_over"] = True
    _game_state["active"] = False

    return {
        "gave_up": True,
        "answer": _game_state["target_word"]
    }


def end_round() -> Dict:
    """
    จบรอบเกม - Mock
    """
    global _game_state

    summary = {
        "won": _game_state["won"],
        "target_word": _game_state["target_word"],
        "total_rounds": _game_state["round"]
    }

    _game_state["active"] = False

    return summary