import customtkinter as ctk
from typing import Dict
from gui.components import create_button, create_label, show

# หน้าคุ่มือ
def create_tutorial_ui(root: ctk.CTk, stack: Dict) -> ctk.CTkFrame:
    frame = ctk.CTkFrame(root)
    frame.grid_rowconfigure(0, weight=0)
    frame.grid_rowconfigure(1, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    # สร้างปุ่มย้อนกลับ
    top_bar = ctk.CTkFrame(frame)
    top_bar.grid(row=0, column=0, sticky="ew")
    create_button(top_bar, text="ย้อนกลับ", 
                command=lambda: show(stack, "Home"), # กลับไปหน้า Home 
                width=120).pack(side="left", padx=10, pady=8)
    
    # เนื้อหาคู่มือ
    content = ctk.CTkFrame(frame, fg_color="transparent")
    content.grid(row=1, column=0, sticky="nsew")

    create_label(content, "คู่มือการเล่นเกม", font=("Sarabun", 24)).pack(pady=(20, 10))

    create_label(
        content,
        "หากผู้เล่นเลือกระดับเสร็จ เวลาจะเริ่มนับถอยหลังทันที\n"
        "ให้ผู้เล่นพิมพ์คำศัพท์ที่เกี่ยวข้องกับหมวดหมู่ที่กำหนดไว้\n"
        "ทางตัวเกมจะบอกลำดับความใกล้เคียงของคำศัพท์ที่ผู้ใช้พิมพ์เข้ามาในลำดับ 1-50\n"
        "ให้ผู้เล่นพิมพ์คำศัพท์ต่อไปเรื่อยๆจนกว่าจะครบเวลา 3 นาที",
        font=("Arial", 16),
        justify="left"
    ).pack(pady=20)

    return frame


