# core/embedding_service.py

import os
import pickle
import numpy as np # สำหรับการเก็บและคำนวณเวกเตอร์ embedding
import logging # แสดง log ข้อมูล, warning, error ใน console
from typing import Dict
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

# โหลดข้อมูล embeddings จากไฟล์ .pkl สำหรับ level คำศัพท์ที่เลือก
def load_embeddings(level, category_templates=None):
    
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

# คืนรายการคำทั้งหมดสำหรับระดับคำศัพท์ที่กำหนด
def get_words(level):

    return _embedding_data[level]["all_words"]

# คืน dictionary ของคำที่จัดหมวดหมู่แล้วสำหรับ level คำศัพท์ที่กำหนด
def get_words_by_category(level) :

    return _embedding_data[level]["words_by_category"]

# คืนค่า embedding vector ของคำที่กำหนด
def get_embedding(level, word):
    
    # หา index ของคำใน embeddings array
    index = _word_to_idx[level].get(word)
    
    # ถ้าไม่พบคำ log warning และ return None
    if (index is None) :
        logger.warning(f"ไม่พบคำ '{word}' ใน embeddings ({level})")
        return None
    
    # คืน embedding vector ของคำนั้น
    return _embedding_data[level]["embeddings"][index]

# คืนชื่อหมวดหมู่ของคำที่กำหนด
def get_category(level, word):
    
    # loop ทุกหมวดหมู่และคำในหมวดนั้น
    for category, words in _embedding_data[level]["words_by_category"].items():
        if word in words:
            # # คืนหมวดหมู่ที่พบ
            return category
    return "unknown" # ถ้าไม่พบคำในทุกหมวด 

# ตรวจสอบว่ามีคำนี้ใน level นั้นหรือไม่
def has_word(level, word) :
    return get_embedding(level, word) is not None
    
# Similarity Computation

# คำนวณ cosine similarity ระหว่างสองคำ
def similarity(level, word_a, word_b):
    
    global _cache_hits, _cache_misses 
    
    # ถ้าคำ target กับคำ input เป็นคำเดียวกัน คืน 1.0 ทันที
    if word_a == word_b:
        return 1.0
    
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
    
    # ถ้าไม่พบคำใดคำหนึ่ง คืน None
    if (embed_a is None or embed_b is None) :
        return None
    # เปลี่ยน "เวกเตอร์ 1 มิติ" ให้กลายเป็น "เมทริกซ์ 2 มิติ" ที่มีเพียงแถวเดียว
    embed_a, embed_b = embed_a.reshape(1, -1), embed_b.reshape(1, -1)
    
    # คำนวณ cosine similarity
    sim = float(cosine_similarity(embed_a, embed_b)[0][0])
    # จำกัดค่าให้อยู่ในช่วง 0.0 - 1.0
    sim = max(0.0, min(1.0, sim))
    # เก็บผลใน cache
    _similarity_cache[cache_key] = sim
    
    return sim

# คำนวณ similarity ที่ปรับน้ำหนักตามความสัมพันธ์ของหมวดหมู่
def adjusted_similarity(level, word_a, word_b):
    
    # ถ้าคำ target กับคำ input เป็นคำเดียวกัน คืน 1.0 ทันที
    if word_a == word_b:
        return 1.0
    # คำนวณ cosine similarity
    base_sim = similarity(level, word_a, word_b)
    if base_sim is None :
        return None
    
    # ดึงหมวดหมู่ของทั้งสองคำ
    cat_a = get_category(level, word_a)
    cat_b = get_category(level, word_b)
    
    # ถ้าคำอยู่ในหมวดเดียวกันคืนต่า similarity เดิม
    if cat_a == cat_b :
        return base_sim
    
    # กำหนดหมวดหมู่ที่แตกต่างกันมาก แยกตามระดับ
    very_different = set()
    
    # level ง่าย: อาหาร กีฬา ห้องเรียน
    if level == "easy" :
        very_different = {
            frozenset(["อาหาร", "กีฬา"]),
            frozenset(["อาหาร", "ห้องเรียน"]),
            frozenset(["กีฬา", "ห้องเรียน"]),
        }
    
    # level ปานกลาง: อาชีพ สัตว์ ร่างกาย สถานที่ ห้องครัว วิชาการ  
    elif level == "medium" :
        very_different = {
            frozenset(["สัตว์", "ห้องครัว"]),
            frozenset(["สัตว์", "อาชีพ"]),
            frozenset(["สัตว์", "วิชาการ"]),
            
            frozenset(["ร่างกาย", "ห้องครัว"]),
            frozenset(["ร่างกาย", "สถานที่"]),
            
            frozenset(["อาชีพ", "ห้องครัว"]),
            frozenset(["วิชาการ", "ห้องครัว"]),
            frozenset(["อาชีพ", "สัตว์"]),
            
            frozenset(["สถานที่", "ร่างกาย"]),
            frozenset(["สถานที่", "สัตว์"]),
        }
    
    # level ยาก: จังหวัด เครื่องดนตรี ห้องนอน ฟาร์มปศุสัตว์ เครื่องใช้ไฟฟ้า ชายทะเล ของเล่น ธรรมชาติ อารมณ์ความรู้สึก
    elif level == "hard" :
        very_different = {
            frozenset(["อารมณ์ความรู้สึก", "เครื่องดนตรี"]),
            frozenset(["อารมณ์ความรู้สึก", "ห้องนอน"]),
            frozenset(["อารมณ์ความรู้สึก", "เครื่องใช้ไฟฟ้า"]),
            frozenset(["อารมณ์ความรู้สึก", "ของเล่น"]),
            frozenset(["อารมณ์ความรู้สึก", "ฟาร์มปศุสัตว์"]),
            
            frozenset(["จังหวัด", "เครื่องดนตรี"]),
            frozenset(["จังหวัด", "ห้องนอน"]),
            frozenset(["จังหวัด", "ของเล่น"]),
            frozenset(["ชายทะเล", "เครื่องดนตรี"]),
            frozenset(["ชายทะเล", "ห้องนอน"]),
            
            frozenset(["ธรรมชาติ", "เครื่องใช้ไฟฟ้า"]),
            frozenset(["ธรรมชาติ", "ห้องนอน"]),
            frozenset(["ธรรมชาติ", "ของเล่น"]),
            
            frozenset(["ฟาร์มปศุสัตว์", "ห้องนอน"]),
            frozenset(["ฟาร์มปศุสัตว์", "เครื่องดนตรี"]),
            
            frozenset(["เครื่องดนตรี", "เครื่องใช้ไฟฟ้า"]),
            frozenset(["เครื่องดนตรี", "ของเล่น"]),
        }
        
    # สร้าง frozenset ของคู่หมวดหมู่ที่กำลังเปรียบเทียบ
    compare_category = frozenset([cat_a, cat_b])
    
    # ปรับน้ำหนักค่า similarity ตามความใกล้เคียงกันของหมวดหมู่
    
    # ถ้าอยู่ในคู่หมวดที่แตกต่างกันมากลดเหลือ 40 % 
    if compare_category in very_different :
        sim_adjusted = base_sim * 0.4
    # ถ้าเป็นหมวดต่างกันทั่วไป ลดเหลือ 70%
    else :
        sim_adjusted = base_sim * 0.7
        
    # จำกัดค่าให้อยู่ในช่วง 0.0 - 1.0    
    sim_adjusted = max(0.0, min(1.0, sim_adjusted))
    # ค่า similarity ที่ถูกปรับแล้ว
    return sim_adjusted

# คำนวณ similarity ของคำหนึ่งเทียบกับคำทั้งหมดในชุด
def similarities_batch(level, word, all_words=None, use_cache=True ):
    
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
        
    # กรองเฉพาะคำที่มีอยู่ใน word_to_idx    
    valid_words = [w for w in all_words if w in _word_to_idx[level]]
    # ถ้าไม่มีคำ valid คืน empty dict
    if not valid_words:
        logger.warning(f"[similarities_batch] No valid words found for level {level}")
        return {}
    
    # ดึง index ของคำทั้งหมดที่ต้องคำนวณ
    indices = [_word_to_idx[level][w] for w in valid_words]
    
    # ตรวจสอบว่า indices ไม่เกินขอบเขตของ embeddings array
    max_idx = len(_embedding_data[level]["embeddings"]) - 1
    safe_indices = [idx for idx in indices if idx <= max_idx]
    
    if not indices :
        return {}
    # ดึง embedding ของคำทั้งหมด
    all_embs = _embedding_data[level]["embeddings"][safe_indices]
    
    # เปลี่ยน "เวกเตอร์ 1 มิติ" ให้กลายเป็น "เมทริกซ์ 2 มิติ" ที่มีเพียงแถวเดียว
    emb_input = emb_input.reshape(1, -1)
    # คำนวณ cosine similarity เป็น array
    sims = cosine_similarity(emb_input, all_embs)[0]
    
    # สร้าง dictionary ของผลลัพธ์
    result = {}

    for i, w in enumerate(valid_words):
        if i < len(sims):
            result[w] = float(sims[i])
    
    # 
    if use_cache and len(all_words) == len(_embedding_data[level]["all_words"]):
        _batch_cache[word] = result.copy()
        
    return result

# คืนรายการคำที่คล้ายกับ `word` มากที่สุด n คำ
def get_top_similar(level, word, n, exclude_self=True):
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

# คำนวณ similarities ล่วงหน้าสำหรับคำทั้งหมด เพื่อเก็บลง cache
def precompute_similarities(level, words_to_cache=None):
    
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
def get_cache_stats() :
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
def get_info(level) :
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