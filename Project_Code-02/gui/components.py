import logging
import customtkinter as ctk
from typing import Dict, Optional

# # สร้าง logger สำหรับจัดการข้อความ
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # ตั้งระดับการบันทึก log เป็น DEBUG (ละเอียดสุด)

# สร้างปุ่ม 
def create_button(parent, text: str, command, **kwargs) -> ctk.CTkButton:
    default_kwargs = {'font': ('Sarabun', 16), # กำหนดฟอนต์และขนาดตัวอักษร
                      'corner_radius': 10,   # มุมโค้งของปุ่ม
                      'height': 50,  # ความสูงของปุ่ม
                      'fg_color': '#1E90FF'} # สีพื้นหลัง (ฟ้า)
    default_kwargs.update(kwargs)
    return ctk.CTkButton(parent, text=text, command=command, **default_kwargs)

# สร้าง label ของข้อความ
def create_label(parent, text: str, **kwargs) -> ctk.CTkLabel:
    default_kwargs = {'font': ('Sarabun', 14), 'text_color': '#000000'}
    default_kwargs.update(kwargs)
    return ctk.CTkLabel(parent, text=text, **default_kwargs)

# # สร้างช่องกรอกข้อความ
def create_entry(parent, placeholder: str = "", **kwargs) -> ctk.CTkEntry:
    default_kwargs = {'font': ('Sarabun', 16), 'height': 40, 'corner_radius': 8}
    default_kwargs.update(kwargs)
    return ctk.CTkEntry(parent, placeholder_text=placeholder, **default_kwargs)

# สร้างแถบแสดงความคืบหน้า
def create_progress_bar(parent, **kwargs) -> ctk.CTkProgressBar:
    default_kwargs = {'height': 20, 'corner_radius': 10}
    default_kwargs.update(kwargs)
    pb = ctk.CTkProgressBar(parent, **default_kwargs)
    pb.set(1.0)
    return pb

# สร้าง Stack สำหรับจัดการ frame ต่าง ๆ ของแอป
def init_stack(root: ctk.CTk) -> Dict:
    stack = {"root": root, # อ้างอิงหน้าต่างหลัก
            "frames": {}, # เก็บ frame ทั้งหมดในรูป dict
            "current": None # เก็บชื่อ frame ที่กำลังแสดงอยู่
            } 
    
    root.grid_rowconfigure(0, weight=1) # ปรับ layout ให้ขยายได้ตามหน้าจอ
    root.grid_columnconfigure(0, weight=1)
    logger.info("Frame stack initialized.") # บันทึกข้อความ log
    return stack

# ลงทะเบียน frame ใหม่เข้าไปใน stack
def register(stack: Dict, name: str, frame: ctk.CTkFrame):
    if name in stack["frames"]:
        logger.error(f"Frame '{name}' already registered.") # ถ้ามีชื่อ frame ซ้ำ จะ error
        raise ValueError(f"Frame '{name}' already registered.")
    frame.grid(row=0, column=0, sticky="nsew") # วาง frame เต็มพื้นที่
    stack["frames"][name] = frame  # เพิ่ม frame เข้าคลัง
    logger.info(f"Frame '{name}' registered.") #  บันทึกข้อความ log

# แสดง frame ที่ต้องการ โดยซ่อน frame อื่น ๆ
def show(stack: Dict, name: str):
    if name not in stack["frames"]: # ถ้าไม่มีชื่อ frame นี้ใน stack ให้ error
        logger.error(f"Frame '{name}' not found.")
        raise KeyError(f"Frame '{name}' not registered.")
    stack["frames"][name].tkraise() # ยก frame ขึ้นมาอยู่ด้านหน้า
    stack["current"] = name # บันทึกชื่อ frame ที่กำลังแสดง
    logger.info(f"Showing frame: {name}")

# ดึงชื่อ frame ปัจจุบันที่กำลังแสดงอยู่
def get_current(stack: Dict) -> Optional[str]:
    return stack.get("current") # คืนค่าเป็นชื่อ frame