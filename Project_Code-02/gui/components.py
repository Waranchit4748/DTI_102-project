import logging
import customtkinter as ctk

# สร้าง logger สำหรับจัดการข้อความ
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG) # ตั้งระดับการบันทึก log เป็น DEBUG (ละเอียดสุด)

# สร้างปุ่ม 
def create_button(parent, text, command, **kwargs):
    default_kwargs = {'font': ('Sarabun', 16), # กำหนดฟอนต์และขนาดตัวอักษร
                      'corner_radius': 10,   # มุมโค้งของปุ่ม
                      'height': 50,  # ความสูงของปุ่ม
                      'fg_color': '#1E90FF'} # สีพื้นหลัง (ฟ้า)
    default_kwargs.update(kwargs)
    return ctk.CTkButton(parent, text=text, command=command, **default_kwargs)

# สร้าง label ของข้อความ
def create_label(parent, text, **kwargs):
    default_kwargs = {'font': ('Sarabun', 14), 'text_color': '#000000'}
    default_kwargs.update(kwargs)
    return ctk.CTkLabel(parent, text=text, **default_kwargs)

# สร้างช่องกรอกข้อความ
def create_entry(parent, placeholder = "", **kwargs):
    default_kwargs = {'font': ('Sarabun', 16), 'height': 40, 'corner_radius': 8}
    default_kwargs.update(kwargs)
    return ctk.CTkEntry(parent, placeholder_text=placeholder, **default_kwargs)

# สร้างแถบแสดงความคืบหน้า
def create_progress_bar(parent, **kwargs):
    default_kwargs = {'height': 20, 'corner_radius': 10}
    default_kwargs.update(kwargs)
    pb = ctk.CTkProgressBar(parent, **default_kwargs)
    pb.set(1.0)
    return pb

# สร้าง Stack สำหรับจัดการ frame ต่าง ๆ ของแอป
def init_stack(root):
    stack = {"root": root, # อ้างอิงหน้าต่างหลัก
            "frames": {}, # เก็บ frame ทั้งหมดในรูป dict
            "current": None # เก็บชื่อ frame ที่กำลังแสดงอยู่
            } 
    
    root.grid_rowconfigure(0, weight=1) # ปรับ layout ให้ขยายได้ตามหน้าจอ
    root.grid_columnconfigure(0, weight=1)
    logger.info("Frame stack initialized.") # บันทึกข้อความ log
    return stack

# ลงทะเบียน frame ใหม่เข้าไปใน stack
def register(stack, name, frame):
    if name in stack["frames"]:
        logger.error(f"Frame '{name}' already registered.") # ถ้ามีชื่อ frame ซ้ำ จะ error
        raise ValueError(f"Frame '{name}' already registered.")
    
    # Grid ทุก frame ไว้ตั้งแต่ต้น (แต่จะซ้อนกัน)
    frame.grid(row=0, column=0, sticky="nsew")
    stack["frames"][name] = frame  # เพิ่ม frame เข้าคลัง
    logger.info(f"Frame '{name}' registered.") #  บันทึกข้อความ log

# แสดง frame ที่ต้องการ โดยซ่อน frame อื่น ๆ
def show(stack, name):
    if name not in stack["frames"]: # ถ้าไม่มีชื่อ frame นี้ใน stack ให้ error
        logger.error(f"Frame '{name}' not found.")
        raise KeyError(f"Frame '{name}' not registered.")
    
    # เรียก on_hidden ก่อน (สำคัญ! ต้องหยุด threads ก่อน)
    if stack["current"]:
        old_frame = stack["frames"].get(stack["current"])
        if old_frame and hasattr(old_frame, 'on_hidden'):
            try:
                old_frame.on_hidden()
                logger.info(f"Called on_hidden() for frame: {stack['current']}")
            except Exception as e:
                logger.error(f"Error calling on_hidden() for {stack['current']}: {e}")
    
    # ยก frame ใหม่ขึ้นมา (ไม่มี flicker เพราะไม่ได้ remove frame เก่า)
    new_frame = stack["frames"][name]
    new_frame.tkraise()
    stack["current"] = name # บันทึกชื่อ frame ที่กำลังแสดง
    logger.info(f"Showing frame: {name}")
    
    # เรียก on_shown function ถ้ามี
    if hasattr(new_frame, 'on_shown'):
        try:
            new_frame.on_shown()
            logger.info(f"Called on_shown() for frame: {name}")
        except Exception as e:
            logger.error(f"Error calling on_shown() for {name}: {e}")

# ดึงชื่อ frame ปัจจุบันที่กำลังแสดงอยู่
def get_current(stack):
    return stack.get("current") # คืนค่าเป็นชื่อ frame