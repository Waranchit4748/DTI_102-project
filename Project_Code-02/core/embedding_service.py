# core/embedding_service.py

import os
import pickle
import numpy as np # สำหรับการเก็บและคำนวณเวกเตอร์ embedding
import logging # แสดง log ข้อมูล, warning, error ใน console
from typing import Dict, List, Optional, Tuple
from sklearn.metrics.pairwise import cosine_similarity # คำนวณ cosine similarity ระหว่างเวกเตอร์
from pathlib import Path # จัดการ path ของไฟล์ให้ทำงานได้ทั้ง Windows / Mac

# Logging setup

logger = logging.getLogger(__name__)
if not logger.handlers:
    # กำหนด log เป็น INFO (จะแสดง INFO, WARNING, ERROR)
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    
# Global State
# เก็บข้อมูล embeddings ของแต่ละระดับ (easy/medium/hard)
_embedding_data: Dict[str, dict] = {} 
# เก็บ mapping คำ -> ดัชนีใน embeddings
_word_to_idx: Dict[str, Dict[str, int]] = {} 
# Cache สำหรับเก็บผลลัพธ์ similarity ของคู่คำ (word_a, word_b)
_similarity_cache: Dict[str, Dict[str, float]] = {} 
# Cache สำหรับเก็บผลลัพธ์ similarity ของคำหนึ่งเทียบกับทุกคำใน batch
_batch_cache: Dict[str, Dict[str, float]] = {} 

# ตัวนับ cache hits/misses
_cache_hits = 0
_cache_misses = 0
# template สำหรับแต่ละ category (เป้น dict จาก precompute_embeddings.py )
CATEGORY_TEMPLATES: Dict[str, str] = {}


# Load and Validate Embeddings

def load_embeddings(level: str, category_templates: Optional[Dict[str,str]] = None) -> None:
    global _embedding_data, _word_to_idx, CATEGORY_TEMPLATES
    
    # ถ้ามี template ใหม่ ส่งเข้ามา -> อัปเดต global
    if category_templates:
        CATEGORY_TEMPLATES = category_templates
    
    # path ของไฟล์ .pkl ที่เก็บ embeddings
    pkl_path = Path("data") / f"{level}.pkl"
    
    # ถ้าไฟล์ไม่พบ error และแนะนำให้รัน precompute_embeddings
    if not pkl_path.exists():
        raise FileNotFoundError(
            f"ไม่พบไฟล์ {pkl_path}\nกรุณารัน: python precompute_embeddings.py --level {level}"
        )
    
    logger.info(f"[Embedding] Loading from {pkl_path}")
    
    # โหลดข้อมูลจากไฟล์ .pkl
    with open(pkl_path, "rb") as f:
        data = pickle.load(f)
    
    # ตรวจสอบว่าไฟล์มี key สำคัญครบหรือไม่    
    required = ["all_words", "embeddings", "words_by_category"]
    for key in required:
        if (key not in data) :
            raise ValueError(f"ข้อมูลใน .pkl ไม่ถูกต้อง (ขาด {key})")
    
    # ตรวจสอบจำนวนคำตรงกับจำนวน embeddings หรือไม่   
    if len(data["all_words"]) != len(data["embeddings"]) :
        raise ValueError("จำนวนคำไม่ตรงกับ embeddings")
    
    # เก็บข้อมูลลง global state
    _embedding_data[level] = data
    
    # สร้าง mapping จากคำ -> index ใน embeddings array
    _word_to_idx[level] = {w: i for i, w in enumerate(data["all_words"])}
    
    # สรุปจำนวนคำ,ขนาดของเวกเตอร์แต่ละคำ
    logger.info(
        f"[Embedding] Loaded {len(data['all_words'])} words "
        f"(dim={data['embeddings'].shape[1]}, model={data.get('model_name','unknown')})"
    )
    
# Basic Getters
def get_words(level: str) -> List[str]:
    '''คืนรายการคำทั้งหมดสำหรับระดับคำศัพท์ที่กำหนด
        level: ("easy", "medium", "hard")
        return: List[str] — รายการคำทั้งหมด
    '''
    return _embedding_data[level]["all_words"]

# คืน dictionary ของคำที่จัดหมวดหมู่แล้วสำหรับ level คำศัพท์ที่กำหนด
def get_words_by_category(level: str) -> Dict[str, List[str]]:
    '''level: ("easy", "medium", "hard")
        return: list ของคำในหมวดนั้น
    '''
    return _embedding_data[level]["words_by_category"]

def get_embedding(level: str, word: str) -> Optional[np.ndarray]:
    # หา index ของคำใน embeddings array
    index = _word_to_idx[level].get(word)
    
    # ถ้าไม่พบคำ log warning และ return None
    if (index is None) :
        logger.warning(f"ไม่พบคำ '{word}' ใน embeddings ({level})")
        return None
    
    # คืน embedding vector ของคำนั้น
    return _embedding_data[level]["embeddings"][index]

def get_category(level: str, word: str) -> str:
    # loop ทุกหมวดหมู่และคำในหมวดนั้น
    for category, words in _embedding_data[level]["words_by_category"].items():
        if word in words:
            # # คืนหมวดหมู่ที่พบ
            return category
    return "unknown" # ถ้าไม่พบคำในทุกหมวด 
    
# Similarity Computation
def scaled_similarity(level, word_a, word_b):
    
    # ความคล้ายกันระหว่าง word_a กับ word_b
    sim = similarity(level, word_a, word_b)
    if sim is None :
       return None
   
    # ดึงหมวดหมู่ของ word_a
    category = get_category(level, word_a)
    # คำนวณ similarity ของ word_a กับทุกคำในหมวดเดียวกัน
    sims_in_category = [similarity(level, word_a, w) 
                        for w in get_words_by_category(level).get(category, [])
    ]
    # หา min และ max ของ similarity ของ word_a กับคำทั้งหมดในหมวดเดียวกัน
    min_s, max_s = min(sims_in_category), max(sims_in_category)
    
    # ถ้าช่วงไม่เป็นศูนย์ ให้ทำ min-max scaling เพื่อปรับ similarity ให้อยู่ระหว่าง 0-1
    if max_s - min_s > 0:
        sim_scaled = (sim - min_s) / (max_s - min_s)
    # ถ้าช่วงเป็นศูนย์ (ทุกค่าเท่ากัน) คืนค่า similarity เดิม
    else:
        sim_scaled = sim
        
    # คืนค่า similarity ที่ปรับสเกลแล้ว
    return sim_scaled

def similarity(level: str, word_a: str, word_b: str) -> Optional[float]:
    
    global _cache_hits, _cache_misses 
    # tuple ของคำสองคำเป็น key ของ cache (เรียงลำดับเพื่อให้ a-b กับ b-a เหมือนกัน)
    cache_key = tuple(sorted([word_a, word_b]))
    
    # ถ้ามีใน cache คืนค่าและเพิ่ม counter hits
    if (cache_key in _similarity_cache) :
        _cache_hits += 1
        return _similarity_cache[cache_key]
    
    # ถ้าไม่เจอใน cache เพิ่ม counter misses
    _cache_misses += 1
    
    # ดึง embedding ของทั้งสองคำ
    embed_a = get_embedding(level, word_a)
    embed_b = get_embedding(level, word_b)
    
    # 
    if (embed_a is None or embed_b is None) :
        return None
    # เปลี่ยน "เวกเตอร์ 1 มิติ" ให้กลายเป็น "เมทริกซ์ 2 มิติ" ที่มีเพียงแถวเดียว
    embed_a, embed_b = embed_a.reshape(1, -1), embed_b.reshape(1, -1)
    
    # คำนวณ cosine similarity
    sim = float(cosine_similarity(embed_a, embed_b)[0][0])
    # เก็บผลใน cache
    _similarity_cache[cache_key] = sim
    
    return sim

def similarities_batch(
    level: str, word: str, all_words: Optional[List[str]] = None, use_cache: bool =True ) -> Dict[str, float] :
    
    global _cache_hits, _cache_misses
    
    # คืนค่า cache ถ้าใช้ cache และ all_words เป็น None (เต็มชุด) และมีใน batch_cache
    if (use_cache and all_words is None and word in _batch_cache ) :
        _cache_hits += 1
        return _batch_cache[word].copy()
    
    _cache_misses += 1
    
    # ดึง embedding ของคำ input
    emb_input = get_embedding(level, word)
    if (emb_input is None ):
        return {}
    
    # ถ้าไม่ได้ระบุ all_words ให้ใช้คำทั้งหมดของระดับนั้น
    if (all_words is None) :
        all_words = _embedding_data[level]["all_words"]
    
    # ดึง index ของคำทั้งหมดที่ต้องคำนวณ
    indices = [i for w, i in _word_to_idx[level].items() if w in all_words]
    if not indices :
        return {}
    # ดึง embedding ของคำทั้งหมด
    all_embs = _embedding_data[level]["embeddings"][indices]
    
    # เปลี่ยน "เวกเตอร์ 1 มิติ" ให้กลายเป็น "เมทริกซ์ 2 มิติ" ที่มีเพียงแถวเดียว
    emb_input = emb_input.reshape(1, -1)
    # คำนวณ cosine similarity เป็น array
    sims = cosine_similarity(emb_input, all_embs)[0]
    
    result = {w: float(sims[i]) for i, w in enumerate(all_words) if w in _word_to_idx[level]}
    if use_cache and len(all_words) == len(_embedding_data[level]["all_words"]):
        _batch_cache[word] = result.copy()
        
    return result

# คืนรายการคำที่คล้ายกับ `word` มากที่สุด n คำ
def get_top_similar(level: str, word: str, n: int = 10, exclude_self: bool = True):
    # คำนวณ similarity กับทุกคำใน level เดียวกัน
    sims = similarities_batch(level, word)
    
    # ถ้าไม่มี similarity คืน empty list
    if not sims:
        return []
    
    # ลบคำตัวเองออกจากผลลัพธ์ ถ้า exclude_self=True
    if (exclude_self and word in sims):
        del sims[word]
    
     # sort ตาม similarity จากมากไปน้อย และตัด n อันดับแรก
    return sorted(sims.items(), key=lambda x: x[1], reverse=True)[:n]

# Cache Management

def precompute_similarities(level: str, words_to_cache: Optional[List[str]] = None):
    
    if (words_to_cache is None):
        words_to_cache = _embedding_data[level]["all_words"]
        
    logger.info(f"Precomputing similarities for {len(words_to_cache)} words...")
    
    # วนลูปผ่านคำทั้งหมดใน words_to_cache เพื่อ precompute similarities
    for i, w in enumerate(words_to_cache, 1):
        if (i % 100 == 0): 
            logger.info(f"  Progress: {i}/{len(words_to_cache)}")
        
        # เรียกฟังก์ชัน similarities_batch เพื่อคำนวณ similarity ของคำนี้กับคำอื่น ๆ เก็บผลลัพธ์ไว้ใน cache (_batch_cache) เพื่อใช้ซ้ำได้
        similarities_batch(level, w, use_cache=True)
    
    logger.info("Precompute completed")

# ล้าง cache ทั้งหมดที่เก็บ similarity และ batch similarity    
def clear_cache():
    
    global _similarity_cache, _batch_cache, _cache_hits, _cache_misses
    # ล้าง dictionary cache ทั้งสองตัว
    _similarity_cache.clear()
    _batch_cache.clear()
    
    # รีเซ็ตตัวนับ hits/misses
    _cache_hits = _cache_misses = 0
    logger.info("Cache cleared")

# คืนค่าข้อมูลสถิติของ cache ทั้งหมด
def get_cache_stats() -> dict :
    total = _cache_hits + _cache_misses
    hit_rate = (_cache_hits / total * 100) if total > 0 else 0
    return {
        "hits": _cache_hits, # จำนวนครั้งที่เจอข้อมูลใน cache
        "misses": _cache_misses, # จำนวนครั้งที่ไม่เจอข้อมูลใน cache
        "hit_rate": f"{hit_rate:.1f}%", # อัตราการเจอ cache เป็น %
        "similarity_cache": len(_similarity_cache), # จำนวนคู่คำที่เก็บไว้ใน similarity cache
        "batch_cache": len(_batch_cache), # จำนวนคำที่เก็บไว้ใน batch cache
    }

# คืนข้อมูลสรุปเกี่ยวกับ embeddings ใน level คำศัพท์ที่กำหนด
def get_info(level: str) -> dict :
    data = _embedding_data[level]
    return {
        "level": level, # คำศัพท์ (easy/medium/hard)
        "total_words": len(data["all_words"]), # จำนวนคำทั้งหมด
        "embedding_dim": data["embeddings"].shape[1], # ขนาดของเวกเตอร์ embedding
        "categories": list(data["words_by_category"].keys()), # รายการหมวดหมู่ทั้งหมด
        "num_categories": len(data["words_by_category"]), # จำนวนหมวดหมู่
        "model_name": data.get("model_name", "unknown"), # ชื่อโมเดลที่ใช้สร้าง embeddings
        **get_cache_stats() # ข้อมูลสถิติ cache จาก get_cache_stats()
    }