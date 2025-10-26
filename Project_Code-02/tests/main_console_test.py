import sys
from core.embedding_service import EmbeddingService

def main():
    print("ทดสอบระบบ Embedding Similarity Console Mode")
    print("------------------------------------------------")

    level = input("เลือกระดับ (easy / medium / hard): ").strip().lower()
    if level not in ["easy", "medium", "hard"]:
        print("ระดับไม่ถูกต้อง")
        sys.exit(1)

    service = EmbeddingService(level)

    while True:
        word_a = input("คำที่ 1: ").strip()
        if word_a.lower() == "exit":
            break

        word_b = input("คำที่ 2: ").strip()
        if word_b.lower() == "exit":
            break

        if not service.has_word(word_a):
            print(f"ไม่พบคำ '{word_a}' ในชุดข้อมูลระดับ {level}")
            continue

        if not service.has_word(word_b):
            print(f"ไม่พบคำ '{word_b}' ในชุดข้อมูลระดับ {level}")
            continue

        sim = service.similarity(word_a, word_b)
        print(f"ความคล้ายระหว่าง '{word_a}' และ '{word_b}': {sim:.4f}\n")

        top_sim = service.get_top_similar(word_a, n=5)
        print(f"คำที่คล้าย '{word_a}' มากที่สุด:")
        for i, (w, s) in enumerate(top_sim, 1):
            print(f"   {i}. {w:<20} {s:.4f}")
        print("-" * 40)

if __name__ == "__main__":
    main()
