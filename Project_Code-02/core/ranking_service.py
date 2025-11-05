import logging
from typing import List, Tuple, Optional
from core.embedding_service import similarities_batch

logger = logging.getLogger(__name__)

#จัดอันดับคำตามความคล้ายจากใกล้ที่สุด - ไกลที่สุด
def rank_words(level, target, all_words , top_n = None):

    # คำนวณ similarity ของ target กับทุกคำใน all_words
    sims = similarities_batch(level, target, all_words)

    # จัดเรียงจากมากไปน้อย
    ranked = sorted(sims.items(), key=lambda x: x[1], reverse=True)

    if top_n:
        return ranked[:top_n]
    return ranked

#คำอยู่ในลำดับที่เท่าไหร่ใน ranked
def get_rank_for_word(word, ranked_list):
    #ลูปเพื่อให้ลำดับที่1ขึ้นก่อน
    for rank, item in enumerate(ranked_list, start=1):
        current_word = item[0]
        if current_word == word:
            return rank
    return None

#คำนวณเปอร์เซ็นของคำว่าอยู่ที่เท่าไหร่
def get_percentile_rank(rank: int, total_words: int) -> float:
    if total_words == 0:
        return 0.0
    return (1 - (rank / total_words)) * 100