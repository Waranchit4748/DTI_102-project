import customtkinter as ctk
from gui.components import create_button, create_label, show

# หน้าคู่มือ
def create_tutorial_ui(root, stack):
    frame = ctk.CTkFrame(root)
    frame.grid_rowconfigure(0, weight=0)
    frame.grid_rowconfigure(1, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    # สร้างปุ่มย้อนกลับ
    top_bar = ctk.CTkFrame(frame, fg_color="white")
    top_bar.grid(row=0, column=0, sticky="ew")
    create_button(top_bar, text="กลับหน้าหลัก", text_color="white", fg_color = "#3B8ED0",
                command=lambda: show(stack, "Home"), # กลับไปหน้า Home 
                width=120).pack(side="left", padx=10, pady=8)
    
    # พื้นที่ตรงกลางเนื้อหาคู่มือ
    content = ctk.CTkFrame(frame, fg_color="white")
    content.grid(row=1, column=0, sticky="nsew")

    create_label(content, "คู่มือการเล่นเกม", font=("Sarabun", 24)).pack(pady=(20, 10))

    create_label(
        content,
        "ผู้เล่นจะเริ่มต้นด้วยการเลือกระดับเกมที่ต้องการ เมื่อเลือกระดับเสร็จ เวลาจะเริ่มนับถอยหลังทันที\n\n"
        "ผู้เล่นต้องพิมพ์คำศัพท์ที่เกี่ยวข้องกับคำเป้าหมายที่เกมกำหนด เช่น หมวดหมู่ผลไม้ สัตว์ อาหาร หรือหมวดหมู่อื่น ๆ\n\n"
        "เกมจะประเมินความใกล้เคียงของคำที่พิมพ์กับคำเป้าหมายตามระดับความยากที่เลือก\n\n"
        "และแสดงลำดับให้ผู้เล่นทราบ เพื่อให้ผู้เล่นสามารถวิเคราะห์คำถัดไปให้ใกล้เคียงคำเป้าหมายมากที่สุด\n\n"
        "ผู้เล่นสามารถพิมพ์คำต่อเนื่องเรื่อย ๆ จนกว่าจะหมดเวลา ซึ่งโดยทั่วไปเวลาที่กำหนดคือ 3 นาที\n\n"
        "เกมจะมีคำใบ้ให้ผู้เล่น จำนวน 3 ครั้ง หากผู้เล่นไม่พิมพ์คำใด ๆ ภายใน 45 วินาทีหลังครั้งล่าสุด\n\n"
        "เกมจะแสดงคำใบ้อัตโนมัติ เมื่อหมดเวลา หากผู้เล่นยังไม่สามารถทายคำเป้าหมายที่ถูกต้อง เกมจะแจ้งคำเฉลยทันที\n\n"
        "ผู้เล่นสามารถนำผลลัพธ์ไปปรับกลยุทธ์และวางแผนคำตอบในรอบต่อไปเพื่อสะสมความสำเร็จ\n\n"
        "เคล็ดลับคือ ควรคิดคำให้หลากหลายและเกี่ยวข้องกับหมวดหมู่ สังเกตลำดับความใกล้เคียง และหลีกเลี่ยงการพิมพ์คำซ้ำ\n\n",
        font=("Sarabun", 14),
        justify="left"
    ).pack(pady=20)

    return frame


