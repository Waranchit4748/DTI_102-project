# scripts/precompute_embeddings.py

'''
Usage :
    python scripts/generate_embeddings.py --level all 
'''

import argparse
import pickle # บันทึกและโหลดข้อมูลในรูปแบบไบนารี (.pkl)
import numpy as np
from pathlib import Path # จัดการ path ของไฟล์ให้ทำงานได้ทั้ง Windows / Mac
import logging # สำหรับแสดง log ระหว่างรันโปรแกรม
from sentence_transformers import SentenceTransformer # โมเดลสำหรับสร้าง embeddings

# CONFIG :
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_MODEL = "sentence-transformers/LaBSE" # ชื่อโมเดลที่ใช้สร้าง embeddings
DEFAULT_BATCH = 64 # จำนวน batch ที่ใช้ encode พร้อมกัน (ให้ไม่กิน RAM มากเกินไป)

# กำหนด "รูปประโยค" สำหรับแต่ละหมวดหมู่ เพื่อสร้าง context ในการฝังความหมายของคำ
CATEGORY_TEMPLATES = {
    "อาหาร": "{word} เป็นอาหารหรือส่วนผสมอาหารที่สามารถปรุงหรือรับประทานได้ มีรสชาติและคุณค่าทางโภชนาการ บางครั้งมีกลิ่นหอม เปรี้ยว หวาน เค็ม หรือเผ็ด",
    "กีฬา": "{word} เป็นการเคลื่อนไหวร่างกายหรือกิจกรรมแข่งขันกีฬาที่ใช้ความแข็งแรง ความเร็ว ทักษะ หรือกลยุทธ์ มักเล่นในสนาม ลาน หรือสระน้ำ",
    "ห้องเรียน": "{word} เป็นวัตถุหรืออุปกรณ์การเรียนที่ใช้ในห้องเรียนหรือโรงเรียน เช่น เครื่องเขียน เฟอร์นิเจอร์ หรืออุปกรณ์สอน ไม่สามารถกินได้และไม่มีชีวิต",
    "อาชีพ": "{word} เป็นอาชีพหรืองานที่มนุษย์ทำเพื่อหารายได้ ใช้ความรู้หรือทักษะเฉพาะด้าน มักมีสถานที่ทำงานและเวลาทำงานที่แน่นอน",
    "สัตว์": "{word} เป็นสิ่งมีชีวิตประเภทสัตว์ที่มีการเคลื่อนไหว หายใจ กินอาหาร ขับถ่าย และสืบพันธุ์ อาจมีขน เกล็ด หรือขนนก บางชนิดเลี้ยงเป็นสัตว์เลี้ยงหรือพบในธรรมชาติ",
    "วิชาการ": "{word} เป็นวิชาหรือสาขาวิชาที่เรียนในสถาบันการศึกษา มีหลักสูตร ตำรา และการสอบวัดผล เช่น วิทยาศาสตร์ คณิตศาสตร์ ภาษา สังคมศึกษา",
    "ห้องครัว": "{word} เป็นอุปกรณ์หรือเครื่องมือที่ใช้ในการปรุงอาหาร เก็บอาหาร หรือทำความสะอาดในครัว ทำจากโลหะ พลาสติก แก้ว หรือไม้ ใช้กับไฟหรือน้ำ",
    "สถานที่": "{word} เป็นสถานที่ ทำเล หรือพื้นที่ที่ผู้คนสามารถเดินทางไป เยี่ยมชม ทำกิจกรรม หรืออาศัยอยู่ มีตำแหน่งที่ตั้งทางภูมิศาสตร์ที่ชัดเจน",
    "ร่างกาย": "{word} เป็นส่วนหนึ่งของร่างกายมนุษย์หรือสัตว์ มีโครงสร้างทางชีววิทยา ทำหน้าที่เฉพาะในร่างกาย เช่น อวัยวะภายใน อวัยวะภายนอก กระดูก กล้ามเนื้อ",
    "จังหวัด": "{word} เป็นจังหวัดหนึ่งในประเทศไทย มีเขตการปกครอง มีที่ว่าการจังหวัด ผู้ว่าราชการจังหวัด และสถานที่ท่องเที่ยวหรือวัฒนธรรมพื้นถิ่นเฉพาะ",
    "เครื่องดนตรี": "{word} เป็นเครื่องมือที่ใช้สำหรับบรรเลงดนตรีหรือเล่นเพลง สร้างเสียงผ่านการตี เป่า ดีด หรือสี มีทั้งเครื่องดนตรีไทยและเครื่องดนตรีสากล",
    "ห้องนอน": "{word} เป็นเฟอร์นิเจอร์หรือสิ่งของที่วางในห้องนอนสำหรับการพักผ่อน นอนหลับ หรือเก็บเสื้อผ้า เช่น เตียง หมอน ตู้เสื้อผ้า โคมไฟข้างเตียง",
    "ฟาร์มปศุสัตว์": "{word} เกี่ยวข้องกับการเลี้ยงสัตว์ในฟาร์ม การทำปศุสัตว์ อุปกรณ์ดูแลสัตว์ หรือผลิตภัณฑ์จากสัตว์ เช่น นม ไข่ เนื้อสัตว์ คอกสัตว์",
    "เครื่องใช้ไฟฟ้า": "{word} เป็นอุปกรณ์หรือเครื่องจักรที่ใช้พลังงานไฟฟ้าในการทำงาน ต้องเสียบปลั๊กหรือใช้แบตเตอรี่ ช่วยอำนวยความสะดวกในบ้านหรือสำนักงาน",
    "ชายทะเล": "{word} เป็นสิ่งที่พบหรือเกี่ยวข้องกับชายหาด ทะเล คลื่น ทราย และกิจกรรมท่องเที่ยวทางทะเล เช่น การว่ายน้ำ ดำน้ำ หรือเล่นกีฬาทางน้ำ",
    "ของเล่น": "{word} เป็นของเล่นหรือของใช้สำหรับความบันเทิงของเด็ก ทำจากพลาสติก ผ้า ไม้ หรือโลหะ ใช้สำหรับการเล่น พัฒนาจินตนาการ หรือฝึกทักษะ",
    "ธรรมชาติ": "{word} เป็นองค์ประกอบทางธรรมชาติที่เกิดขึ้นเองตามธรรมชาติ ไม่ได้สร้างโดยมนุษย์ เช่น ภูเขา แม่น้ำ ป่าไม้ สภาพอากาศ หรือปรากฏการณ์ทางธรรมชาติ",
    "อารมณ์ความรู้สึก": "{word} เป็นอารมณ์หรือความรู้สึกทางจิตใจของมนุษย์ ไม่สามารถจับต้องได้ แต่แสดงออกผ่านสีหน้า ท่าทาง คำพูด หรือพฤติกรรม เช่น ดีใจ เศร้า โกรธ กลัว",
}

# LOAD WORDS :
def load_words_from_txt(txt_path: str):
    '''อ่านไฟล์ .txt แล้วแยกคำศัพท์ออกตามหมวดหมู่'''
    
    all_words = [] # เก็บคำทั้งหมด
    all_contexts = [] # เก็บประโยค context ที่สร้างจาก template
    words_by_category = {} # เก็บ mapping หมวดหมู่ -> คำในหมวดนั้น

    # เปิดพื่ออ่านข้อมูล
    with open(txt_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f,1):
            line = line.strip() # ลบช่องว่าง / \n ออกจากต้นและท้ายบรรทัด
            if (not line) or (line.startswith("#")):
                continue
            
            # แต่ละบรรทัดควรมีรูปแบบ "หมวดหมู่|คำ,คำ,คำ"
            if ("|" not in line) :
                logger.warning(f"Line {line_num}: Missing '|' delimiter")
                continue
            
            category, words_str = line.split("|", 1)
            # แยกคำในบรรทัดด้วยเครื่องหมายจุลภาค ได้ list ของคำ
            word_list = [w.strip() for w in words_str.split(",") if w.strip()]
            words_by_category[category.strip()] = word_list
            
            for word in word_list:
                # ดึง template สำหรับหมวดหมู่ที่กำหนดจาก CATEGORY_TEMPLATES
                template = CATEGORY_TEMPLATES.get(category)
                
                # ไม่พบ template สำหรับหมวดหมู่นั้น
                if not template :
                    logger.warning(f"หมวด '{category}' ไม่มี template ใน CATEGORY_TEMPLATES — ใช้ค่าเริ่มต้นแทน")
                    # กำหนด template เริ่มต้น เพื่อให้โค้ดยังคงทำงานได้
                    template = "{word} เป็นคำศัพท์ในหมวด {category}"
                    
                # สร้างประโยค context จาก template เช่น “ส้ม เป็นอาหารหรือวัตถุดิบ...”
                all_words.append(word)
                all_contexts.append(template.format(word=word, category=category))
    
    logger.info(f"พบ {len(all_words)} คำ ใน {len(words_by_category)} หมวดหมู่")
    return all_words, all_contexts, words_by_category

# GENERATE EMBEDDINGS

def generate_embedding(sentences, model_name=DEFAULT_MODEL, batch_size=DEFAULT_BATCH):
    '''ใช้โมเดล SentenceTransformer สร้างเวกเตอร์ embedding สำหรับประโยคทั้งหมด'''
    
    logger.info(f"โหลดโมเดล: {model_name}")
    model = SentenceTransformer(model_name)
    logger.info("โหลดโมเดลสำเร็จ")
    
    logger.info(f"สร้าง embeddings สำหรับ {len(sentences)} คำ ...")
    embeddings = model.encode(
        sentences,
        batch_size=batch_size, 
        show_progress_bar=True, # แสดงแถบสถานะขณะประมวลผล
        convert_to_numpy=True, # แปลงผลลัพธ์เป็น numpy array
        normalize_embeddings=True # เวกเตอร์แต่ละตัวจะมีความยาวเท่ากับ 1 คำนวณ similarity ด้วย cosine ได้แม่นยำ
    )
    
    logger.info(f"สร้าง embeddings เสร็จสิ้น (shape: {embeddings.shape})")
    return embeddings

# PRECOMPUTE EMBEDDINGS
def precompute_embeddings(level):
    '''อ่านคำจากไฟล์ -> สร้าง embeddings -> บันทึกเป็น .pkl'''
    
    # กำหนด path ของไฟล์คำศัพท์และไฟล์ .pkl
    txt_path = Path(f"data/{level}.txt")
    pkl_path = Path(f"data/{level}.pkl")      
    
    # ตรวจสอบว่าไฟล์คำศัพท์มีอยู่หรือไม่
    if not txt_path.exists():
        raise FileNotFoundError(f"ไม่พบไฟล์ {txt_path}\nกรุณาสร้างไฟล์คำศัพท์ก่อน")
    
    # โหลดคำและ context 
    all_words, all_contexts, words_by_category = load_words_from_txt(txt_path)
    # สร้าง embeddings สำหรับทุกคำ
    embeddings = generate_embedding(all_contexts)
    
    # รวมข้อมูลทั้งหมดไว้ใน dictionary
    data = {
        "all_words": all_words, # รายการคำทั้งหมด
        "embeddings": embeddings, # embeddings ของแต่ละคำ
        "words_by_category": words_by_category, # แยกคำตามหมวดหมู่
        "level": level, # ระดับความยาก
        "model_name": DEFAULT_MODEL, 
        "embedding_dim": embeddings.shape[1], # ขนาด embedding
        "use_context": True 
    }
    
    # ถ้ายังไม่มีโฟลเดอร์ data/ ให้สร้างใหม่
    pkl_path.parent.mkdir(parents=True, exist_ok=True)
    # บันทึกข้อมูลเป็นไฟล์ .pkl
    with open(pkl_path, "wb") as f :
        pickle.dump(data, f)
    
    # คำนวณขนาดไฟล์ .pkl เป็น MB
    size_mb = pkl_path.stat().st_size / 1024 / 1024
    logger.info(f"บันทึก {pkl_path} เรียบร้อย ({size_mb:.2f} MB)")
    
    # แสดงจำนวนคำในแต่ละหมวดหมู่
    logger.info("สรุปจำนวนคำต่อหมวดหมู่:")
    for cat, words in words_by_category.items():
        logger.info(f"   - {cat}: {len(words)} คำ")
    return data

# VALIDATE PKL
def validate_pkl(level):
    '''ตรวจสอบว่าไฟล์ .pkl ที่สร้างไว้ถูกต้องหรือไม่'''
    
    # กำหนด path ของไฟล์ .pkl ตาม level
    pkl_path = Path(f"data/{level}.pkl")
    
    # ตรวจสอบว่ามีไฟล์ .pkl หรือไม่
    if not pkl_path.exists():
        logger.error(f"ไม่พบไฟล์ {pkl_path}")
        return False
    
    try: 
        # โหลดข้อมูลจากไฟล์ .pkl
        with open(pkl_path, "rb") as f:
            data = pickle.load(f)
        
        # ตรวจสอบว่ามี key ที่จำเป็นครบถ้วนหรือไม่
        required_keys = ["all_words", "embeddings", "words_by_category"]
        for key in required_keys:
            if key not in data:
                logger.error(f"Missing key: {key}") # แจ้งว่าไฟล์ขาดข้อมูล
                return False
        
        # ตรวจสอบจำนวนคำตรงกับจำนวน embeddings
        if len(data["all_words"]) != len(data["embeddings"]) :
            logger.error("จำนวนคำไม่ตรงกับจำนวน embeddings")
            return False
        
        # ถ้าผ่านทุกอย่าง — แสดงข้อมูลสรุป
        logger.info(f"ไฟล์ {pkl_path} ถูกต้อง")
        logger.info(f"   - Words: {len(data['all_words'])}") # จำนวนคำทั้งหมด
        logger.info(f"   - Categories: {len(data['words_by_category'])}") # จำนวนหมวดหมู่
        logger.info(f"   - Embedding shape: {data['embeddings'].shape}") # shape ของ embeddings
        logger.info(f"   - Model: {data.get('model_name', 'N/A')}") # โมเดลที่ใช้สร้าง embeddings
        return True
    except Exception as e:
        return False

# MAIN
def main():
    '''ส่วนหลักของโปรแกรม — จัดการ argument และเรียก precompute/validate'''
    
    # สร้าง parser สำหรับอ่าน argument จาก command line
    parser = argparse.ArgumentParser(description="Precompute Thai word embeddings")
    # เพิ่ม argument --level เพื่อกำหนดระดับคำศัพท์ (easy, medium, hard, all)
    parser.add_argument("--level", type=str, choices=["easy", "medium", "hard", "all"], default="all", help="ระดับคำศัพท์")
    # เพิ่ม argument --validate เป็น flag (True/False) สำหรับตรวจสอบไฟล์ .pkl แทนการสร้างใหม่
    parser.add_argument("--validate", action="store_true", help="ตรวจสอบไฟล์ .pkl แทนการสร้างใหม่")    
    
    args = parser.parse_args()
    
    # ถ้าคำสั่งรัน scripts เป็น python scripts\precompute_embeddings.py --level all ให้กับไฟล์ระดับความยากทั้งหมด
    # ถ้าเลือกเฉพาะระดับ → list จะมีแค่ระดับนั้น
    levels = ["easy", "medium", "hard"] if args.level == "all" else [args.level]
    
    for level in levels:
        logger.info(f"\n{'='*60}")
        logger.info(f"Level: {level.upper()}")
        logger.info(f"{'='*60}\n")
        
        # ถ้า user ส่ง flag --validate ตรวจสอบไฟล์ .pkl แทนการสร้างใหม่
        if args.validate:
            validate_pkl(level)
        else: 
            try:
                # สร้าง embeddings และบันทึกเป็น .pkl
                precompute_embeddings(level)
            except Exception as e :
                # ถ้าเกิดข้อผิดพลาดใด ๆ → ข้ามไปยัง level ถัดไป
                continue

if __name__ == "__main__":
    main()