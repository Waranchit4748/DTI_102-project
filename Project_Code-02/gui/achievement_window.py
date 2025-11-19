import customtkinter as ctk
from typing import Dict
from core.achievement_service import load_achievements, ACHIEVEMENT_DEFINITIONS, get_unlocked
from gui.components import create_label, create_button, show

def create_achievements_ui(root: ctk.CTk, stack: Dict):
    # โหลดสถานะ Achievement
    load_achievements()

    frame = ctk.CTkFrame(root, fg_color="#F8FAFC") 
    frame.grid_rowconfigure(0, weight=0) 
    frame.grid_rowconfigure(1, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    # ======= ส่วนบน (Top Bar) =======
    top_bar = ctk.CTkFrame(frame, fg_color="white", corner_radius=0)
    top_bar.grid(row=0, column=0, sticky="ew", pady=(0, 2))
    create_button(
        top_bar,
        text="กลับหน้าหลัก",
        text_color="white",
        fg_color="#3B8ED0",  # น้ำเงินสดใส
        hover_color="#3B8ED0",
        command=lambda: show(stack, "Home"),
        width=120,
    ).pack(side="left", padx=15, pady=10)

    create_label(
        top_bar,
        "ความสำเร็จของคุณ",
        font=("Sarabun", 22, "bold"),
        text_color="#1E293B"
    ).pack(side="left", padx=20)

    scroll_frame = ctk.CTkScrollableFrame(frame, fg_color="#F8FAFC") # สร้างเฟรมที่มันเลื่อนได้
    scroll_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10) # เว้นขอบกว้าง 20พิกเซล ยาว10พิกเซล

    unlocked = get_unlocked() # เรียกฟังก์ชั่นการปลดล็อคด่านที่ผ่านแล้วมาจากของออม แล้วคืนค่าผลบันทึกทั้งหมด

    # ตรวจสอบสถานะว่ามีด่านที่ผ่านแล้วไหมถ้าไม่มีแสดงว่าไม่มีความสำเร็จ ถ้ามีด่านปลดล้อคแล้วก็ไม่แสดงอะไร แสดงการ์ดความสำเร็จที่ผ่าน
    if not unlocked:
        create_label(
            scroll_frame, #ทำให้มันเลื่อนได้
            "ยังไม่มีความสำเร็จที่ปลดล็อก",
            font=("Sarabun", 16),
            text_color="#5E6774"
        ).pack(pady=40)

    # ======= แสดงรายการ Achievement =======
    for id, info in ACHIEVEMENT_DEFINITIONS.items():
        unlocked_flag = id in unlocked #ตรวจสอบว่าด่านนี้ปลดล้อคยัง ถ้าปลดล้อคแล้วแสดงผลว่าปลดล้อคและเปลี่ยนสีข้อความและพื้นหลัง

        if unlocked_flag: #ถ้าผ่านแสดงสีกรอบและข้อความตามที่กำหนด
            card_color = "#E0F2FE"
            text_color = "#0F172A"
        else: #ถ้าไม่ผ่านแสดงสีกรอบและข้อความตามที่กำหนด
            card_color = "#F1F5F9"
            text_color = "#5E6774"

        # สร้างการ์ดของแต่ละความสำเร็จ
        card = ctk.CTkFrame(scroll_frame, fg_color=card_color, corner_radius=12) # กำหนดความโค้งมนเป้น12
        card.pack(fill="x", pady=6, padx=10)

        # ชื่อ Achievement โหลดจากออมมา
        create_label(
            card,
            info["name"],
            font=("Sarabun", 18, "bold"),
            text_color=text_color,#เปลี่ยนสีตามสถานะที่กำหนดไว้
            anchor="w" # "w" คือซ้ายสุดของการ์ด
        ).pack(anchor="w", padx=15, pady=(8, 0))

        # คำอธิบาย โหลดจากออมมา
        create_label(
            card,
            info["description"],
            font=("Sarabun", 14),
            text_color=text_color, #เปลี่ยนสีตามสถานะที่กำหนดไว้
            anchor="w" # "w" คือซ้ายสุดของการ์ด
        ).pack(anchor="w", padx=15, pady=(0, 6))

        # สถานะ
        if unlocked_flag: # ปลดล้อคแล้วตัวอักษรสีฟ้า
            status = "ปลดล็อกแล้ว"
            color = "#0284C7"
        else: # ยังไม่ปลดล้อคแล้วตัวอักษรสีเทา
            status = "ยังไม่ปลดล็อก"
            color = "#5E6774"

        create_label(
            card,
            status,
            font=("Sarabun", 13),
            text_color=color
        ).pack(anchor="e", padx=15, pady=(0, 8))  # "e" คือขวาสุดของการ์ด

    return frame
