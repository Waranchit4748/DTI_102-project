import logging
import customtkinter as ctk
from gui.components import init_stack, register, show
from gui.home_window import create_home_ui, create_play_ui
from gui.tutorial_window import create_tutorial_ui

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
def register_frames(stack: dict, root: ctk.CTk):
    frames = {
        "Home": create_home_ui(root, stack), # หน้าหลักของเกม
        "Play": create_play_ui(root, stack), # หน้าสำหรับเล่นเกม
        "tutorial": create_tutorial_ui(root, stack),  #หน้าคุ่มือ
    }
    
    # วนเพิ่มแต่ละ frame เข้าสู่ stack
    for name, frame in frames.items():
        register(stack, name, frame)

    show(stack, "Home") # แสดงหน้าแรกเป็นหน้า Home
    logging.info("All frames registered.")
    return stack

# ฟังก์ชันหลักในการรันเกม
def run_game():
    setup_logging() # เรียกใช้ระบบ logging
    logging.info("Starting Word Guess Game...")

    root = ctk.CTk()
    root.title("Word Guess Challenge") # ตั้งชื่อหน้าต่างเกม
    root.geometry("700x700") # กำหนดขนาดหน้าต่าง
    root.resizable(False, False)

    load_fonts() # โหลดฟอนต์
    apply_theme(root) # ตั้งค่าธีม

    stack = init_stack(root)
    register_frames(stack, root) # สร้างและลงทะเบียน Frame

    root.mainloop() # เริ่มลูปหลักของ GUI (แสดงหน้าต่างเกม)
    logging.info("Game closed.")

# จุดเริ่มต้นของโปรแกรม
if __name__ == "__main__":
    run_game() # เรียกให้โปรแกรมเริ่มทำงาน
