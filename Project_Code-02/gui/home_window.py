import logging
import customtkinter as ctk
from gui.components import create_button, create_label, show
from typing import Dict
 
# สร้างตัว logger สำหรับเก็บ log ของไฟล์นี้ (เช่น ใช้ดูว่าเริ่มเกมระดับใด)
logger = logging.getLogger(__name__)
 
# หน้าหลัก (Home Screen)
def create_home_ui(root: ctk.CTk, stack: Dict):
    # สร้างเฟรมหลักของหน้า Home (พื้นหลังสีขาว)
    frame = ctk.CTkFrame(root, fg_color="white")
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
 
    # สร้าง container สำหรับวาง widget ภายในหน้า
    container = ctk.CTkFrame(frame, fg_color="white")
    container.grid(row=0, column=0)
 
    # ข้อความชื่อเกม
    title = create_label(container, "เดาให้ได้ ถ้าเธอแน่จริง",
                         font=('Sarabun', 40, 'bold'),
                         text_color="black", fg_color="white")
    title.pack(pady=(0, 200))
 
    # ปุ่มเริ่มเล่นเกม — เมื่อคลิกจะเปลี่ยนหน้าไปยัง "Play"
    create_button(frame,
                text="เริ่มเล่นเกม",
                command=lambda: show(stack, "Play"), # กดสลับไปยังหน้าจอ Play
                width=220,
                border_width=0,
                fg_color="#3B8ED0"
                ).place(relx=0.5, rely=0.55, anchor="center")
   
     # ปุ่มคุ่มือ
    create_button(
        frame,
        text="คู่มือการเล่นเกม",
        command=lambda: show(stack, "tutorial"), #ถ้ากดปุ่มจะไหปหน้า tutorial_window
        width=220,
        border_width=0,
        fg_color="#3B8ED0"
    ).place(relx=0.5, rely=0.65, anchor="center")
 
    # ปุ่มตั่งค่า
    create_button(
        frame,
        text="ตั้งค่า",
        command=lambda: show(stack, "settings"), #ถ้ากดปุ่มจะไหปหน้า settings_window
        width=220,
        border_width=0,
        fg_color="#3B8ED0"
    ).place(relx=0.5, rely=0.75, anchor="center")
 
    # ปุ่มหน้าความสำเร็จ
    create_button(
        frame,
        text="ความสำเร็จ",
        command=lambda: show(stack, "achievement"), #ถ้ากดปุ่มจะไหปหน้า achievement_window
        width=220,
        border_width=0,
        fg_color="#3B8ED0"
    ).place(relx=0.5, rely=0.85, anchor="center")
   
    return frame
 
# หน้าเลือกระดับความยาก (Play Screen)
def create_play_ui(root: ctk.CTk, stack: Dict):
    # เฟรมหลักของหน้า Play
    frame = ctk.CTkFrame(root, fg_color="white")
    frame.grid_rowconfigure(0, weight=0)
    frame.grid_rowconfigure(1, weight=1)
    frame.grid_columnconfigure(0, weight=1)
 
    # แถบด้านบนที่มีปุ่มย้อนกลับไปหน้า Home
    top_bar = ctk.CTkFrame(frame, fg_color="white")
    top_bar.grid(row=0, column=0, sticky="ew")
    create_button(top_bar, text="ย้อนกลับ", text_color="white", fg_color="#3B8ED0",
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
                  command=lambda: start_game(stack, "ง่าย"), width=220).pack(pady=8)
    create_button(inner, text="ระดับปานกลาง", text_color="white", fg_color="#3B8ED0",
                  command=lambda: start_game(stack, "ปานกลาง"), width=220).pack(pady=8)
    create_button(inner, text="ระดับยาก", text_color="white", fg_color="#3B8ED0",
                  command=lambda: start_game(stack, "ยาก"), width=220).pack(pady=8)
 
    return frame
 
# ฟังก์ชันเริ่มเกม (เมื่อเลือกความยากแล้ว)
def start_game(stack, difficulty):
    # บันทึกข้อความใน log ว่าผู้เล่นเลือกความยากระดับใด
    logger.info(f"Starting game with difficulty: {difficulty}")
 
    # เปลี่ยนหน้าไปยัง "Main" ซึ่งเป็นหน้าหลักของเกม
    show(stack, "Main")