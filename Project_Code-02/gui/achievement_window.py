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
        text="← ย้อนกลับ",
        text_color="white",
        fg_color="#3B82F6",  # น้ำเงินสดใส
        hover_color="#2563EB",
        command=lambda: show(stack, "Home"),
        width=120,
    ).pack(side="left", padx=15, pady=10)

    create_label(
        top_bar,
        "🏆 ความสำเร็จของคุณ",
        font=("Sarabun", 22, "bold"),
        text_color="#1E293B"
    ).pack(side="left", padx=20)

    # ======= ส่วนกลาง (Scrollable Area) =======
    scroll_frame = ctk.CTkScrollableFrame(frame, fg_color="#F8FAFC")
    scroll_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

    unlocked = get_unlocked()

    if not unlocked:
        create_label(
            scroll_frame,
            "ยังไม่มีความสำเร็จที่ปลดล็อก",
            font=("Sarabun", 16),
            text_color="#5E6774"
        ).pack(pady=40)

    # ======= แสดงรายการ Achievement =======
    for ach_id, ach_info in ACHIEVEMENT_DEFINITIONS.items():
        unlocked_flag = ach_id in unlocked

        card_color = "#E0F2FE" if unlocked_flag else "#F1F5F9"  # สีพื้นหลังต่างกัน
        text_color = "#0F172A" if unlocked_flag else "#5E6774"

        card = ctk.CTkFrame(scroll_frame, fg_color=card_color, corner_radius=12)
        card.pack(fill="x", pady=6, padx=10)

        # ชื่อ Achievement โหลดจากออมมา
        create_label(
            card,
            ach_info["name"],
            font=("Sarabun", 18, "bold"),
            text_color=text_color,
            anchor="w"
        ).pack(anchor="w", padx=15, pady=(8, 0))

        # คำอธิบาย โหลดจากออมมา
        create_label(
            card,
            ach_info["description"],
            font=("Sarabun", 14),
            text_color=text_color,
            anchor="w"
        ).pack(anchor="w", padx=15, pady=(0, 6))

        # สถานะ
        status = "✅ ปลดล็อกแล้ว" if unlocked_flag else "🔒 ยังไม่ปลดล็อก"
        create_label(
            card,
            status,
            font=("Sarabun", 13, "italic"),
            text_color="#0284C7" if unlocked_flag else "#5E6774"
        ).pack(anchor="e", padx=15, pady=(0, 8))

    return frame
