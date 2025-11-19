import customtkinter as ctk
import logging
from gui.components import create_button, show
 
logger = logging.getLogger(__name__)
 
def create_summary_ui(root, stack):
    frame = ctk.CTkFrame(root, fg_color="white")
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
   
    container = ctk.CTkFrame(frame, fg_color="white")
    container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    container.grid_columnconfigure(0, weight=1)
 
    # หัวข้อผลการเล่น
    result_label = ctk.CTkLabel(
        container,
        text="สรุปผลการเล่น",
        font=("Sarabun", 32, "bold"),
        text_color="#3B8ED0"
    )
    result_label.pack(pady=(10, 5))
 
    # สถานะ (ชนะ/แพ้)
    status_label = ctk.CTkLabel(
        container,
        text="",
        font=("Sarabun", 24, "bold")
    )
    status_label.pack(pady=(5, 10))
 
    # กรอบแสดงคำตอบ
    answer_frame = ctk.CTkFrame(container, fg_color="#f0f0f0", corner_radius=10)
    answer_frame.pack(pady=10, padx=20, fill="x")
 
    answer_title = ctk.CTkLabel(
        answer_frame,
        text="คำตอบที่ถูกต้อง:",
        font=("Sarabun", 18)
    )
    answer_title.pack(pady=(10, 5))
 
    answer_word = ctk.CTkLabel(
        answer_frame,
        text="",
        font=("Sarabun", 36, "bold"),
        text_color="#3B8ED0"
    )
    answer_word.pack(pady=(5, 10))
 
    # กรอบสถิติ
    stats_frame = ctk.CTkFrame(container, fg_color="white")
    stats_frame.pack(pady=10, fill="x")
    stats_frame.grid_columnconfigure((0, 1, 2), weight=1)
 
    guess_count_label = ctk.CTkLabel(stats_frame, text="0\nครั้งที่ทาย", font=("Sarabun", 18))
    guess_count_label.grid(row=0, column=0, padx=20, pady=20)
 
    time_used_label = ctk.CTkLabel(stats_frame, text="00:00\nเวลาที่ใช้", font=("Sarabun", 18))
    time_used_label.grid(row=0, column=1, padx=10, pady=10)
 
    hints_used_label = ctk.CTkLabel(stats_frame, text="0/3\nคำใบ้", font=("Sarabun", 18))
    hints_used_label.grid(row=0, column=2, padx=10, pady=10)
 
    # ปุ่มด้านล่าง
    button_frame = ctk.CTkFrame(container, fg_color="white")
    button_frame.pack(pady=10)
    
    # ฟังก์ชันเริ่มเกมใหม่
    def restart_same_level():
        from core.game_manager import game_state, start_game as init_game
        
        try:
            difficulty = game_state.get('level', 'easy')
            logger.info(f"[RESTART] Difficulty: {difficulty}")
            
            # เริ่มเกมใหม่
            init_game(difficulty)
            
            # รีเซ็ต UI
            if "Main" in stack["frames"]:
                main_frame = stack["frames"]["Main"]
                if hasattr(main_frame, 'reset_game'):
                    main_frame.reset_game(difficulty)
                    logger.info("[RESTART] UI reset completed")
            
            # ไปหน้าเกม
            show(stack, "Main")
            
        except Exception as e:
            logger.error(f"[RESTART] Failed: {e}")
            show(stack, "Play")
 
    # ปุ่มกลับไปเล่นอีกครั้ง
    play_again_btn = create_button(
        button_frame,
        text="เล่นอีกครั้ง",
        command=restart_same_level,
        width=200,
        fg_color="#3B8ED0"
    )
    play_again_btn.grid(row=0, column=0, padx=10)
 
    # ปุ่มกลับไปหน้าเลือกระดับ
    back_btn = create_button(
        button_frame,
        text="เลือกระดับความยาก",
        command=lambda: show(stack, "Play"),
        width=200,
        fg_color="gray"
    )
    back_btn.grid(row=0, column=1, padx=10)
 
    # ฟังก์ชันอัปเดตข้อมูลบนหน้า
    def update_summary(result_data):
       
        result = result_data.get('result', 'unknown')
        target = result_data.get('target', '?')
        category = result_data.get('target_category', 'ไม่ระบุ')
        guesses = result_data.get('guesses', [])
        duration = result_data.get('duration_sec', 0)
        hints = result_data.get('hints_used', 0)
 
        if result == 'win':
            status_label.configure(text="ยินดีด้วย! คุณทายถูก!", text_color="green")
            answer_word.configure(text=f'"{target}"  ({category})', text_color="#3B8ED0")
 
        elif result == 'timeout':
            status_label.configure(text="หมดเวลา!", text_color="red")
            answer_word.configure(text=f'"{target}"  ({category})', text_color="#D9534F")
 
        elif result == 'giveup' or result == 'give_up':
            status_label.configure(text="คุณยอมแพ้", text_color="red")
            answer_word.configure(text=f'"{target}"  ({category})', text_color="#D9534F")
 
        else:
            status_label.configure(text="เกมจบแล้ว", text_color="gray")
            answer_word.configure(text=f'"{target}"  ({category})', text_color="#3B8ED0")
 
        guess_count_label.configure(text=f"{len(guesses)}\nครั้งที่ทาย")
 
        mins, secs = divmod(duration, 60)
        time_used_label.configure(text=f"{mins:02d}:{secs:02d}\nเวลาที่ใช้")
 
        hints_used_label.configure(text=f"{hints}/3\nคำใบ้")
 
        logger.info(f"Summary updated: {result}, target={target}, guesses={len(guesses)}")
 
    frame.update_summary = update_summary
    return frame
 