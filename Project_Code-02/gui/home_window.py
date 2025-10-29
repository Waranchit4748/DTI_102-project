import logging
import customtkinter as ctk
from typing import Dict
from gui.components import create_button, create_label, show
from PIL import Image, ImageTk
import os

# สร้าง logger สำหรับบันทึกข้อความ
logger = logging.getLogger(__name__)

'''ASSETS_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "assets"))
BG_IMAGE_FILENAME = "bg_play.png"

# ภาพพื้นหลังของหน้าจอ
def _load_bg_image(root: ctk.CTk, width=700, height=700):
    path = os.path.join(ASSETS_DIR, BG_IMAGE_FILENAME)
    if not os.path.exists(path):
        logger.warning(f"Background image not found at: {path}")
        return None, (0, 0)
    try:
        img = Image.open(path).convert("RGBA") # เปิดภาพและแปลงให้รองรับความโปร่งใส
        img = img.resize((width, height), Image.LANCZOS) # ปรับขนาดภาพให้พอดีกับหน้าต่าง
        photo = ImageTk.PhotoImage(img) # แปลงภาพให้ใช้ใน Tkinter ได้
        return photo, (width, height)
    except Exception:
        logger.exception("Failed to load background image")
        return None, (0, 0)'''

# สร้างหน้าแรกของเกม
def create_home_ui(root: ctk.CTk, stack: Dict) -> ctk.CTkFrame:
    frame = ctk.CTkFrame(root, fg_color="transparent") # สร้างเฟรมหลักของหน้า Home
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    # โหลดและแสดงภาพพื้นหลัง
    '''photo, _ = _load_bg_image(root)
    if photo:
        bg = ctk.CTkLabel(frame, image=photo, text="")
        bg.image = photo
        bg.place(relx=0.5, rely=0.5, anchor="center", relwidth=1.0, relheight=1.0)'''
    
    # สร้างปุ่มเริ่มเล่นเกม
    create_button(frame, 
                text="เริ่มเล่นเกม", 
                command=lambda: show(stack, "Play"), # กดสลับไปยังหน้าจอ Play
                width=220, 
                border_width=0, 
                fg_color="#3B8ED0"
                ).place(relx=0.5, rely=0.65, anchor="center")
    
    return frame

# สร้างหน้าเลือกระดับความยากของเกม
def create_play_ui(root: ctk.CTk, stack: Dict) -> ctk.CTkFrame:
    frame = ctk.CTkFrame(root) # เฟรมหลักของหน้า "Play"
    frame.grid_rowconfigure(0, weight=0)
    frame.grid_rowconfigure(1, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    # สร้างปุ่มย้อนกลับ
    top_bar = ctk.CTkFrame(frame)
    top_bar.grid(row=0, column=0, sticky="ew")
    create_button(top_bar, text="ย้อนกลับ", 
                command=lambda: show(stack, "Home"), # กลับไปหน้า Home 
                width=120).pack(side="left", padx=10, pady=8)

    # พื้นที่หลักของหน้าจอ
    center = ctk.CTkFrame(frame)
    center.grid(row=1, column=0, sticky="nsew")
    center.pack_propagate(False) # ป้องกันการย่อขนาดอัตโนมัติ

    # เฟรมย่อยด้านใน
    inner = ctk.CTkFrame(center, fg_color="transparent")
    inner.place(relx=0.5, rely=0.5, anchor="center")
    
    # ข้อความหัวข้อ
    create_label(inner, "เลือกระดับความยาก", font=("Sarabun", 18)).pack(pady=(0, 12))

    # สร้างปุ่มเลือกระดับความยาก 3 ระดับ
    create_button(inner, text="ระดับง่าย", fg_color="#4CAF50", 
                command=lambda: start_game(stack, "ง่าย"), width=220).pack(pady=8)
    create_button(inner, text="ระดับปานกลาง", fg_color="#FFA500", 
                command=lambda: start_game(stack, "ปานกลาง"), width=220).pack(pady=8)
    create_button(inner, text="ระดับยาก", fg_color="#FF5733", 
                command=lambda: start_game(stack, "ยาก"), width=220).pack(pady=8)

    return frame

# เริ่มเกมตามระดับความยากที่เลือก
def start_game(stack: Dict, difficulty: str):
    logger.info(f"Starting game with difficulty: {difficulty}") # บันทึกระดับความยากลง Log
    show(stack, "Main") # เปลี่ยนไปยังหน้าเกมหลัก
