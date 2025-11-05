'''import sys
from core.embedding_service import EmbeddingService

import sys 
from core import embedding_service

def main():
    print("ทดสอบระบบ Embedding Similarity Console Mode")
    print("------------------------------------------------")
    
    level = input("เลือกระดับ (easy / medium / hard): ").strip().lower()
    if level not in ["easy", "medium", "hard"]:
        print("❌ ระดับไม่ถูกต้อง")
        sys.exit(1)
    
    embedding_service.load_embeddings(level)
    print(f"โหลด embeddings สำหรับระดับ '{level}' สำเร็จ\n")
    
    while True:
        print("=== เมนูหลัก ===")
        print("1. คำนวณความคล้ายระหว่าง 2 คำ")
        print("2. แสดงคำที่คล้ายที่สุด (Top Similar Words)")
        print("3. ดูสถานะ Cache (Cache Stats)")
        print("4. เคลียร์ Cache")
        print("0. ออกจากโปรแกรม")
        choice = input("เลือกเมนู: ").strip()
        
        if choice == "0" :
            print("ออกจากโปรแกรม...")
            break
        
        elif choice == "1" :
            word_a = input("คำที่ 1: ").strip()
            word_b = input("คำที่ 2: ").strip() 
            sim = embedding_service.similarity(level, word_a, word_b)
            
            if sim is not None:
                print(f"ความคล้ายระหว่าง '{word_a}' และ '{word_b}': {sim:.4f}")
            else:
                print("ไม่สามารถคำนวณได้ (อาจไม่พบคำใน dataset)")
            print("-" * 50)
            
        elif choice == "2":
            word = input("พิมพ์คำที่ต้องการดูความคล้าย: ").strip()
            top_sim = embedding_service.get_top_similar(level, word, n=5)
            if not top_sim:
                print(f"ไม่พบคำ '{word}' ใน embeddings")
            else :
                print(f"คำที่คล้าย '{word}' มากที่สุด:")
                for i, (w, s) in enumerate(top_sim, 1):
                    print(f"   {i}. {w:<20} {s:.4f}")
            
            print("-"*50)
        
        elif choice == "3":
            stats = embedding_service.get_cache_stats()
            print(" สถานะ Cache ปัจจุบัน:")
            for k, v in stats.items():
                print(f"   {k:<20}: {v}")
            print("-" * 50)
            
        elif choice == "4":
            embedding_service.clear_cache()
            print("ล้าง Cache เรียบร้อยแล้ว")
            print("-" * 50)
        
        else: 
            print("ไม่พบเมนูนี้ กรุณาเลือกใหม่\n")

if __name__ == "__main__":
    main()
'''