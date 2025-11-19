import customtkinter as ctk
from typing import Dict
from gui.components import create_button, create_label, show
from core.settings_manager import load_config, save_config, set_volume


def load_current_settings():
    config = load_config()
    return {
        "theme": config["display"].get("theme", "dark"),
        "sound_enabled": config["audio"].get("sound_enabled", True),
        "volume": config["audio"].get("volume", 0.5),
    }

#สร้างหน้าการตั้งค่า
def create_settings_ui(root: ctk.CTk, stack: Dict) -> ctk.CTkFrame:
    frame = ctk.CTkFrame(root, fg_color="#FFFFFF")
    frame.grid_rowconfigure(1, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    settings = load_current_settings()
    sound_var = ctk.BooleanVar(value=settings["sound_enabled"])
    volume_var = ctk.DoubleVar(value=settings["volume"])

    #แสดงว่าเปิดหรือปิดเสียงอยู่
    def toggle_sound():
        print(f"[UI] Sound {'enabled' if sound_var.get() else 'disabled'}")

    #ปรับระดับเสียงตามการเลื่อน
    def update_volume(value):
        set_volume(float(value))
        print(f"[UI] Volume: {float(value):.2f}")

    #กดปุ่มยันทึกแล้วบันทึกการตัั้งค่า
    def save_settings():
        config = load_config()
        config["audio"]["sound_enabled"] = sound_var.get()
        config["audio"]["volume"] = volume_var.get()
        save_config(config)
        print("[UI] Settings saved")

    #ปุ่มกลับ
    top_bar = ctk.CTkFrame(frame, fg_color="#FFFFFF", corner_radius=0)
    top_bar.grid(row=0, column=0, sticky="ew")

    create_button(top_bar, text="กลับหน้าหลัก",
                  command=lambda: show(stack, "Home"),
                  width=140).pack(side="left", padx=15, pady=10)

    content = ctk.CTkScrollableFrame(frame, fg_color="transparent")
    content.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

    create_label(content, "การตั้งค่า", font=("Sarabun", 26, "bold")).pack(pady=(10, 20))

    #สวิตช์เปิด/ปิดเสียง
    sound_box = ctk.CTkFrame(content, fg_color="#E2FAFF", corner_radius=12)
    sound_box.pack(fill="x", pady=10, padx=5)
    create_label(sound_box, "เสียง (Sound):", font=("Sarabun", 18)).pack(pady=(10, 5))
    ctk.CTkSwitch(sound_box, text="เปิดเสียง",
                  variable=sound_var,
                  command=toggle_sound).pack(pady=(0, 10))

    #ระดับเสียง
    volume_box = ctk.CTkFrame(content, fg_color="#E2FAFF", corner_radius=12)
    volume_box.pack(fill="x", pady=10, padx=5)
    create_label(volume_box, "ระดับเสียง (Volume):", font=("Sarabun", 18)).pack(pady=(10, 5))
    ctk.CTkSlider(volume_box,
                  from_=0, to=1,
                  variable=volume_var,
                  command=update_volume,
                  width=250).pack(pady=(0, 10))

    return frame
