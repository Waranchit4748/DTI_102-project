import logging
import os
import customtkinter as ctk
from gui.components import init_stack, register, show
from gui.home_window import create_home_ui, create_play_ui
from gui.main_window import create_game_ui
from gui.tutorial_window import create_tutorial_ui
from gui.settings_window import create_settings_ui
from gui.achievement_window import create_achievements_ui
 
 
# ตั้งค่าระบบ Logging สำหรับบันทึกข้อมูลการทำงานของโปรแกรม
def setup_logging():
    logging.basicConfig(
        level=logging.INFO, # กำหนดระดับความสำคัญของข้อความที่จะแสดง
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', # รูปแบบของข้อความ log
        handlers=[logging.FileHandler('game.log', encoding='utf-8'),
                  logging.StreamHandler()] # แสดง log บนหน้าคอนโซล
    )
    logging.info("Logging initialized.") # แจ้งว่าการตั้งค่า logging เสร็จสมบูรณ์
 
# โหลดฟอนต์ที่ต้องใช้ในเกม
def load_fonts():
    logging.info("Loading fonts...")
    fonts = ['Arial']  # รายชื่อฟอนต์ที่ต้องโหลด
    for font in fonts:
        logging.info(f"Font loaded: {font}") # แสดงข้อความเมื่อโหลดแต่ละฟอนต์
    return fonts
 
# ตั้งค่าธีม (สีและสไตล์) ของโปรแกรม
def apply_theme(root: ctk.CTk):
    logging.info("Applying theme...")
    try:
        ctk.set_default_color_theme("blue")
    except Exception:
        logging.debug("Default color theme not found, using built-in theme.")
 
# ลงทะเบียนและสร้าง Frame หลักของโปรแกรม
def register_frames(root, stack):
    frames = {
        "Home": create_home_ui(root, stack),   # หน้าหลักของเกม
        "Play": create_play_ui(root, stack),   # หน้าเลือกระดับความยาก
        "tutorial": create_tutorial_ui(root, stack),  #หน้าคุ่มือ
        "settings": create_settings_ui(root, stack),  #หน้าตั้งค่า
        "achievement": create_achievements_ui(root, stack),  #หน้าความสำเร็จ
        "Main": create_game_ui(root, stack)    # หน้าเล่นเกม
    }
   
    # วนเพิ่มแต่ละ frame เข้าสู่ stack
    for name, frame in frames.items():
        register(stack, name, frame)
 
    show(stack, "Home") # แสดงหน้าแรกเป็นหน้า Home
    logging.info("All frames registered.")
    return stack

# ลบไฟล์ชั่วคราวเมื่อปิดเกม
def cleanup_on_exit():
    for file in ["history.json", "achievements.json"]:
        if os.path.exists(file):
            try:
                os.remove(file)
                logging.info(f"Deleted {file}")
            except Exception as e:
                logging.error(f"Failed to delete {file}: {e}")
        else:
            logging.debug(f"{file} not found")

# จัดการเมื่อปิดหน้าต่าง
def on_closing(root):
    logging.info("Closing game window...")
    cleanup_on_exit()
    root.destroy()
 
# ฟังก์ชันหลักในการรันเกม
def run_game():
    setup_logging() # เรียกใช้ระบบ logging
    logging.info("Starting Word Guess Game...")
 
    root = ctk.CTk()
    root.title("เกมเดาให้ได้ ถ้าเธอแน่จริง") # ตั้งชื่อหน้าต่างเกม
    root.geometry("700x700") # กำหนดขนาดหน้าต่าง
    root.resizable(False, False)
 
    load_fonts() # โหลดฟอนต์
    apply_theme(root) # ตั้งค่าธีม
 
    stack = init_stack(root)
    register_frames(root, stack) # สร้างและลงทะเบียน Frame

    # เริ่มเล่นเพลง
    initialize_music()
    
    root.protocol("WM_DELETE_WINDOW", lambda: on_closing(root))
    root.mainloop() # เริ่มลูปหลักของ GUI (แสดงหน้าต่างเกม)
    logging.info("Game closed.")
 
# เริ่มต้นของโปรแกรม
if __name__ == "__main__":
    run_game() # เรียกให้โปรแกรมเริ่มทำงาน