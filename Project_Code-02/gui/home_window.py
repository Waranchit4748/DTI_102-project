import logging
import customtkinter as ctk
from gui.components import create_button, create_label, show
from core import settings_manager
from core.settings_manager import load_config, save_config
 
# สร้างตัว logger สำหรับเก็บ log ของไฟล์นี้ (เช่น ใช้ดูว่าเริ่มเกมระดับใด)
logger = logging.getLogger(__name__)
 
# หน้าหลัก (Home Screen)
def create_home_ui(root, stack):
    # สร้างเฟรมหลักของหน้า Home (พื้นหลังสีขาว)
    frame = ctk.CTkFrame(root, fg_color="white")
    frame.grid_rowconfigure(0, weight=0)  # top_bar ไม่ขยาย
    frame.grid_rowconfigure(1, weight=1)  # container ขยายเต็มพื้นที่
    frame.grid_columnconfigure(0, weight=1)
    
    config = load_config()
    sound_var = ctk.BooleanVar(value=config.get("sound_enabled", True))
 
    # ฟังก์ชันเปิด/ปิดเสียง
    def toggle_sound():
        enabled = sound_var.get()
 
        # บันทึกสถานะลง config
        config = load_config()
        config["sound_enabled"] = enabled
        save_config(config)
 
        if enabled:
            # เปิดเสียง
            if settings_manager._music_player:
                settings_manager._music_player.play()
                print("[UI] Music playing")
            else:
                # ถ้าไม่มี music_player ให้เรียกฟังก์ชันเล่นเพลง
                settings_manager.play_music()
        else:
            # ปิดเสียง
            if settings_manager._music_player:
                settings_manager._music_player.pause()
                print("[UI] Music paused")
 
        print(f"[UI] Sound {'enabled' if enabled else 'disabled'}")
 
    # แถบด้านบน
    top_bar = ctk.CTkFrame(frame, fg_color="white")
    top_bar.grid(row=0, column=0, sticky="ew")
 
    # กรอบสวิตช์สวยๆ
    sound_frame = ctk.CTkFrame(top_bar, fg_color="#E2FAFF", corner_radius=12)
    sound_frame.pack(side="right", padx=10, pady=8)
 
    # ใส่สวิตช์เข้าไปในกรอบ
    ctk.CTkSwitch(sound_frame,
                text="เสียงเพลง",
                variable=sound_var,
                command=toggle_sound,
                font=("Sarabun", 18),
                width=80,
                height=50
                ).pack(padx=10, pady=8)
    
    # สร้าง container สำหรับวาง widget ภายในหน้า
    container = ctk.CTkFrame(frame, fg_color="white")
    container.grid(row=1, column=0, sticky="nsew")  # อยู่ใต้ top_bar และขยายเต็ม
 
    # ข้อความชื่อเกม
    title = create_label(container, "เดาให้ได้ ถ้าเธอแน่จริง",
                         font=('Sarabun', 40, 'bold'),
                         text_color="black", fg_color="white")
    title.place(relx=0.5, rely=0.3, anchor="center")
 
    # ปุ่มเริ่มเล่นเกม — เมื่อคลิกจะเปลี่ยนหน้าไปยัง "Play"
    create_button(frame,
                  text="เริ่มเล่นเกม",
                  command=lambda: show(stack, "Play"),
                  width=220,
                  border_width=0,
                  fg_color="#3B8ED0"
                 ).place(relx=0.5, rely=0.55, anchor="center")
   
    # ปุ่มคู่มือ
    create_button(frame,
                  text="คู่มือการเล่นเกม",
                  command=lambda: show(stack, "tutorial"),
                  width=220,
                  border_width=0,
                  fg_color="#3B8ED0"
                 ).place(relx=0.5, rely=0.65, anchor="center")
 
    # ปุ่มความสำเร็จ
    create_button(frame,
                  text="ความสำเร็จ",
                  command=lambda: show(stack, "achievement"),
                  width=220,
                  border_width=0,
                  fg_color="#3B8ED0"
                 ).place(relx=0.5, rely=0.75, anchor="center")
   
    return frame
 
# หน้าเลือกระดับความยาก (Play Screen)
def create_play_ui(root, stack):
    # เฟรมหลักของหน้า Play
    frame = ctk.CTkFrame(root, fg_color="white")
    frame.grid_rowconfigure(0, weight=0)
    frame.grid_rowconfigure(1, weight=1)
    frame.grid_columnconfigure(0, weight=1)
 
    # แถบด้านบนที่มีปุ่มย้อนกลับไปหน้า Home
    top_bar = ctk.CTkFrame(frame, fg_color="white")
    top_bar.grid(row=0, column=0, sticky="ew")
    create_button(top_bar, text="กลับหน้าหลัก", text_color="white", fg_color="#3B8ED0",
                  command=lambda: show(stack, "Home"), width=120).pack(side="left", padx=10, pady=8)
    
    # พื้นที่ตรงกลางของหน้า
    center = ctk.CTkFrame(frame, fg_color="white")
    center.grid(row=1, column=0, sticky="nsew")
 
    # เฟรมภายใน ใช้จัดวางให้อยู่ตรงกลางพอดี
    inner = ctk.CTkFrame(center, fg_color="transparent")
    inner.place(relx=0.5, rely=0.5, anchor="center")
 
    # ข้อความหัวข้อ “เลือกระดับความยาก”
    create_label(inner, "เลือกระดับความยาก", font=("Sarabun", 18)).pack(pady=(0, 12))
 
    # ปุ่มเลือกระดับความยากแต่ละแบบ (ง่าย / ปานกลาง / ยาก)
    create_button(inner, text="ระดับง่าย", text_color="white", fg_color="#3B8ED0",
                  command=lambda: start_game(stack, "easy"), width=220).pack(pady=8)
    create_button(inner, text="ระดับปานกลาง", text_color="white", fg_color="#3B8ED0",
                  command=lambda: start_game(stack, "medium"), width=220).pack(pady=8)
    create_button(inner, text="ระดับยาก", text_color="white", fg_color="#3B8ED0",
                  command=lambda: start_game(stack, "hard"), width=220).pack(pady=8)
 
    return frame
 
# ฟังก์ชันเริ่มเกม (เมื่อเลือกความยากแล้ว)
def start_game(stack, difficulty):
    # บันทึกข้อความใน log ว่าผู้เล่นเลือกความยากระดับใด
    logger.info(f"Starting game with difficulty: {difficulty}")
 
    from core.game_manager import start_game as init_game
    
    try:
        # เริ่มเกมใหม่ตามระดับที่เลือก
        game_info = init_game(difficulty)
        logger.info(f"Game initialized: {game_info}")
        
        # เรียก reset_game_ui ของ Main frame เพื่อรีเซ็ต UI
        if "Main" in stack["frames"]:
            main_frame = stack["frames"]["Main"]
            if hasattr(main_frame, 'reset_game'):
                main_frame.reset_game(difficulty)
        
        # สลับไปหน้าเกม
        show(stack, "Main")
 
    except Exception as e:
        logger.error(f"Failed to start game: {e}", exc_info=True)
        # แสดง error dialog ที่นี้