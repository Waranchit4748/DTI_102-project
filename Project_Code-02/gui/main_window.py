import customtkinter as ctk
import threading
import time
import logging
from queue import Queue

# นำเข้า game_manager แทนการใช้ mock data
from core.game_manager import check_guess, get_hint, give_up, get_game_state, handle_timeout
from gui.components import show

# สร้างตัว logger สำหรับเก็บ log ของไฟล์นี้ (เช่น ใช้ดูว่าเริ่มเกมระดับใด)
logger = logging.getLogger(__name__)

# สร้าง UI หลักของเกม พร้อมเชื่อมต่อกับ game_manager
def create_game_ui(root, stack):
    frame = ctk.CTkFrame(root, fg_color="white")
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)

    # เฟรมด้านใน (container)
    container = ctk.CTkFrame(frame, fg_color="white")
    container.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
    container.grid_columnconfigure(0, weight=1)

    # ตัวจับเวลา (แสดงตัวเลขนับถอยหลัง)
    timer_label = ctk.CTkLabel(container, text="เวลา: 03:00", font=("Sarabun", 24, "bold"))
    timer_label.pack(pady=(10, 5))

    # แถบแสดงเวลาที่เหลือ (progress bar)
    timer_progress = ctk.CTkProgressBar(container, fg_color="white")
    timer_progress.set(1.0)
    timer_progress.pack(fill="x", padx=40, pady=(0, 10))

    # กล่องกรอกคำตอบ
    input_frame = ctk.CTkFrame(container, fg_color="white")
    input_frame.pack(pady=(5, 10))

    # ช่องพิมพ์คำตอบ
    entry = ctk.CTkEntry(input_frame, width=350, placeholder_text="พิมพ์คำตอบที่นี่", font=("Sarabun", 16))
    entry.grid(row=0, column=0, padx=5)

    # ปุ่มส่งคำตอบ
    submit_btn = ctk.CTkButton(
        input_frame, text="ส่งคำตอบ", width=120,
        text_color="white", fg_color="#3B8ED0", hover_color="#3B8ED0",
        border_width=0, font=("Sarabun", 16)
    )
    submit_btn.grid(row=0, column=1, padx=5)

    # ปุ่มคำใบ้ / ยอมแพ้
    button_frame = ctk.CTkFrame(container, fg_color="white")
    button_frame.pack(pady=(5, 10))

    hint_btn = ctk.CTkButton(
        button_frame, text="คำใบ้", width=220,
        text_color="black", fg_color="yellow", hover_color="yellow",
        border_width=0, font=("Sarabun", 16)
    )
    hint_btn.grid(row=0, column=0, padx=5)

    give_up_btn = ctk.CTkButton(
        button_frame, text="ยอมแพ้", width=220,
        text_color="white", fg_color="red", hover_color="red",
        border_width=0, font=("Sarabun", 16)
    )
    give_up_btn.grid(row=0, column=1, padx=5)

    # คำใบ้ / ข้อความตอบกลับ
    feedback_label = ctk.CTkLabel(container, text="", font=("Sarabun", 18))
    feedback_label.pack(pady=(5, 10))

    # ตัวนับจำนวนคำใบ้
    hint_counter_label = ctk.CTkLabel(container, text="คำใบ้: 0/3", font=("Sarabun", 18))
    hint_counter_label.pack()

    # หัวข้อประวัติการทาย
    history_label = ctk.CTkLabel(container, text="ประวัติการทายคำของคุณ", font=("Sarabun", 18, "bold"))
    history_label.pack(pady=(10, 5))

    # พื้นที่แสดงประวัติ (เลื่อนดูได้)
    ranking_frame = ctk.CTkScrollableFrame(container, width=500, height=250, fg_color="white")
    ranking_frame.pack(pady=(5, 10))

    # ================= State Variables =================
    state = {
        'timer_running': False,
        'last_guess_time': None,
        'lock': threading.Lock(),
        'history_items': {},  # dict[word] = {'widget': widget, 'score': float, 'rank': int}
        'ui_queue': Queue(),
        'timer_thread': None,
        'auto_hint_thread': None
    }

    # ================= Helper Functions =================
    # ประมวลผล UI updates จาก queue (เรียกจาก main thread)
    # Code จากปัญญาประดิษฐ์
    def process_ui_queue(): 
        try: 
            while not state['ui_queue'].empty(): 
                action, data = state['ui_queue'].get_nowait() 
                
                if action == "update_timer": 
                    try: 
                        timer_label.configure(text=data['text'])
                        timer_progress.configure(progress_color=data['color']) 
                        timer_progress.set(data['progress']) 
                    except: 
                        # Widget ถูก destroy แล้ว
                        pass 
                    
                elif action == "timeout": 
                    # ไปหน้า summary ทันทีเมื่อหมดเวลา
                    show_summary(data['result']) 
                    return  # หยุดการ process ต่อ
                    
                elif action == "auto_hint": 
                    try: 
                        feedback_label.configure( 
                            text=f"คำใบ้อัตโนมัติ: {data['hint']}", 
                            text_color="blue" 
                        )
                        hint_counter_label.configure(text=f"คำใบ้: {data['hints_used']}/3") 
                    except: 
                        pass 
                    
        except Exception as e: 
            logger.error(f"Error processing UI queue: {e}") 
        
        # เรียกตัวเองอีกครั้งหลัง 100ms
        with state['lock']:
            timer_running = state['timer_running']
        
        if timer_running and frame.winfo_exists():
            root.after(100, process_ui_queue)

    # แปลงวินาทีเป็นรูปแบบ mm:ss
    def format_time(seconds):
        mins, secs = divmod(seconds, 60)
        return f"{mins:02d}:{secs:02d}"

    # แสดงหน้าสรุปผลพร้อมข้อมูล
    def show_summary(result_data):
        # หยุด threads ก่อนเปลี่ยนหน้า
        with state['lock']:
            state['timer_running'] = False
        
        # ล้าง UI queue อย่างรวดเร็ว
        while not state['ui_queue'].empty():
            try:
                state['ui_queue'].get_nowait()
            except:
                break
        
        # อัพเดตข้อมูลสรุปก่อน (ระหว่างที่หน้าเกมยังแสดงอยู่)
        if "Summary" in stack["frames"]:
            summary_frame = stack["frames"]["Summary"]
            if hasattr(summary_frame, 'update_summary'):
                # อัพเดตข้อมูล
                summary_frame.update_summary(result_data)
                # บังคับให้ render ทันที
                summary_frame.update()
        
        # เปลี่ยนหน้าทันที (ข้อมูลพร้อมแล้ว)
        show(stack, "Summary")
        
        # รอให้ threads หยุดจริงๆ
        if state['timer_thread'] and state['timer_thread'].is_alive():
            state['timer_thread'].join(timeout=0.1)

    # ================= Timer Functions =================
    # เริ่มจับเวลา
    # Code จากปัญญาประดิษฐ์
    def start_timer(duration=180): 
        with state['lock']: 
            state['timer_running'] = True 
        
        def countdown(): 
            remaining = duration 
            while remaining >= 0: 
                with state['lock']: 
                    if not state['timer_running']: 
                        break 
                
                # คำนวณ progress และสี
                progress = remaining / duration 
                if progress >= 0.7: 
                    color = "green" 
                elif progress >= 0.4: 
                    color = "orange" 
                else: 
                    color = "red" 
                
                # ส่งข้อมูลไปยัง UI queue
                state['ui_queue'].put(("update_timer", { 
                    'text': f"เวลา: {format_time(remaining)}", 
                    'progress': progress, 
                    'color': color 
                }))
                
                if remaining == 0:
                    # หมดเวลา
                    result = handle_timeout()
                    state['ui_queue'].put(("timeout", {'result': result}))
                    with state['lock']:
                        state['timer_running'] = False
                    break
                    
                time.sleep(1)
                remaining -= 1 
        
        state['timer_thread'] = threading.Thread(target=countdown, daemon=True)
        state['timer_thread'].start()
        
        # เริ่ม process UI queue
        root.after(100, process_ui_queue)

    # หยุดจับเวลา
    def stop_timer():
        with state['lock']:
            state['timer_running'] = False
        
        # รอให้ thread หยุดอย่างรวดเร็ว (timeout สั้น)
        if state['timer_thread'] and state['timer_thread'].is_alive():
            state['timer_thread'].join(timeout=0.1)

    # ================= Auto Hint Functions =================
    # เริ่มระบบ auto hint
    def start_auto_hint(): 
        def check_idle():
            while True:
                with state['lock']:
                    if not state['timer_running']:
                        break
                
                current_time = time.time()
                
                with state['lock']:
                    last_guess = state['last_guess_time']
                
                # ถ้าไม่เคยทาย ให้นับจากเวลาเริ่มเกม
                if last_guess is None:
                    game_state = get_game_state()
                    if game_state.get('time_elapsed', 0) >= 45:
                        # แสดงคำใบ้อัตโนมัติ
                        result = get_hint()
                        if result.get('status') == 'ok':
                            state['ui_queue'].put(("auto_hint", {
                                'hint': result.get('hint', ''),
                                'hints_used': result.get('hints_used', 0)
                            }))
                            logger.info(f"[AUTO-HINT] Triggered after 45s idle")
                        
                        # รีเซ็ตเวลา
                        with state['lock']:
                            state['last_guess_time'] = current_time
                
                # ถ้าเคยทายแล้ว ให้นับจากครั้งล่าสุด
                elif current_time - last_guess >= 45:
                    result = get_hint()
                    if result.get('status') == 'ok':
                        state['ui_queue'].put(("auto_hint", {
                            'hint': result.get('hint', ''),
                            'hints_used': result.get('hints_used', 0)
                        }))
                        logger.info(f"[AUTO-HINT] Triggered after 45s idle")
                    
                    with state['lock']:
                        state['last_guess_time'] = current_time
                
                time.sleep(5)  # เช็คทุก 5 วินาที
        
        state['auto_hint_thread'] = threading.Thread(target=check_idle, daemon=True)
        state['auto_hint_thread'].start()

    # ================= History Management =================
    # สร้าง widget แถวประวัติ
    def create_history_row(word, score, rank, idx):
        row = ctk.CTkFrame(ranking_frame, fg_color="white")
        
        # ลำดับ
        idx_label = ctk.CTkLabel(row, text=f"{idx}.", width=30, anchor="w", text_color="black")
        idx_label.pack(side="left")

        # คำที่ทาย
        guess_label = ctk.CTkLabel(row, text=word, width=100, anchor="w", text_color="black")
        guess_label.pack(side="left")

        # แถบแสดงความคล้าย
        similarity_percent = score * 100
        
        bar = ctk.CTkProgressBar(row, width=200)
        bar.set(score)
        
        if similarity_percent >= 80:
            bar.configure(progress_color="green")
        elif similarity_percent >= 50:
            bar.configure(progress_color="orange")
        else:
            bar.configure(progress_color="red")
        bar.pack(side="left", padx=10)

        # เปอร์เซ็นต์แสดงผล
        percent_label = ctk.CTkLabel(row, text=f"{similarity_percent:.1f}%", width=60)
        percent_label.pack(side="left")
        
        # อันดับ (ถ้ามี)
        if rank:
            rank_label = ctk.CTkLabel(row, text=f"#{rank}", width=50, text_color="gray")
            rank_label.pack(side="left")
        
        return row

    # แสดงประวัติการทายใหม่ (Optimized version)
    def refresh_history():
        # ดึงข้อมูลจาก game_manager
        game_state = get_game_state()
        guesses = game_state.get('guesses', [])
        
        # เรียงตาม score จากมากไปน้อย
        sorted_guesses = sorted(guesses, key=lambda x: x.get('score', 0), reverse=True)
        
        # เช็คว่ามีคำใหม่หรือไม่
        new_words = set(g['word'] for g in sorted_guesses) - set(state['history_items'].keys())
        
        if new_words:
            # มีคำใหม่ - ต้อง rebuild ทั้งหมดเพราะลำดับเปลี่ยน
            for widget in ranking_frame.winfo_children():
                widget.pack_forget()
            
            # อัปเดต history_items
            for guess in sorted_guesses:
                word = guess['word']
                if word not in state['history_items']:
                    state['history_items'][word] = {
                        'score': guess.get('score', 0),
                        'rank': guess.get('rank'),
                        'widget': None
                    }
            
            # แสดงใหม่ตามลำดับ
            for idx, guess in enumerate(sorted_guesses, 1):
                word = guess['word']
                item = state['history_items'][word]
                
                # สร้าง widget ถ้ายังไม่มี หรือใช้ของเดิม
                if item['widget'] is None:
                    item['widget'] = create_history_row(word, item['score'], item['rank'], idx)
                else:
                    # อัปเดตลำดับ
                    for child in item['widget'].winfo_children():
                        if isinstance(child, ctk.CTkLabel):
                            text = child.cget("text")
                            if text.endswith("."):
                                child.configure(text=f"{idx}.")
                                break
                
                item['widget'].pack(fill="x", pady=3, padx=10)

    # ================= Game Actions =================
    # ส่งคำตอบ
    def submit_guess():
        text = entry.get().strip()
        entry.delete(0, 'end')
        
        if not text:
            return
        
        # อัพเดตเวลาที่ทายครั้งล่าสุด
        with state['lock']:
            state['last_guess_time'] = time.time()
        
        # ส่งคำทายไปยัง game_manager
        result = check_guess(text)
        
        # ตรวจสอบว่า result ไม่ใช่ None
        if result is None:
            feedback_label.configure(text="เกิดข้อผิดพลาดในการตรวจสอบคำตอบ", text_color="red")
            logger.error(f"[SUBMIT_GUESS] check_guess returned None for word: {text}")
            return
        
        # อัพเดตประวัติ
        refresh_history()
        
        # แสดงผลตามสถานะที่ได้รับ
        status = result.get('status')
        
        if status == "ok":
            if result.get('is_win'):
                # ไปหน้า summary ทันทีเมื่อชนะ
                show_summary(result)
            else:
                score_percent = result.get('score', 0) * 100
                rank = result.get('rank', '?')
                feedback_label.configure(
                    text=f"ความคล้าย: {score_percent:.1f}% (อันดับ #{rank}) - {result.get('message', '')}", 
                    text_color="orange"
                )
        elif status == "unknown_word":
            feedback_label.configure(text=result.get('message', 'ไม่พบคำนี้ในพจนานุกรม'), text_color="red")
        elif status == "already_guessed":
            feedback_label.configure(text=result.get('message', 'คุณทายคำนี้ไปแล้ว'), text_color="orange")
        elif status == "timeout":
            # ไปหน้า summary ทันทีเมื่อหมดเวลา
            show_summary(result)
        else:
            feedback_label.configure(text=result.get('message', 'เกิดข้อผิดพลาด'), text_color="red")

    # คำใบ้
    def show_hint():
        result = get_hint()
        
        status = result.get('status')
        hints_used = result.get('hints_used', 0)
        
        hint_counter_label.configure(text=f"คำใบ้: {hints_used}/3")
        
        if status == "ok":
            feedback_label.configure(text=f"{result.get('hint', '')}", text_color="blue")
        elif status == "limit_reached":
            feedback_label.configure(text=result.get('message', 'คำใบ้หมดแล้ว!'), text_color="red")
        else:
            feedback_label.configure(text=result.get('message', 'ไม่สามารถให้คำใบ้ได้'), text_color="red")

    # ยอมแพ้
    def give_up_clicked():
        result = give_up()
        
        # ไปหน้า summary ทันทีโดยไม่แสดงเฉลยบนหน้าเกม
        show_summary(result)

    # รีเซ็ตเกม
    def reset_game(difficulty="easy"):
        logger.info(f"[RESET] Starting reset for difficulty: {difficulty}")
       
        # 1. หยุด threads ก่อน
        with state['lock']:
            state['timer_running'] = False
       
        if state['timer_thread'] and state['timer_thread'].is_alive():
            state['timer_thread'].join(timeout=0.5)
       
        # 2. ล้าง UI queue
        while not state['ui_queue'].empty():
            try:
                state['ui_queue'].get_nowait()
            except:
                break
       
        # 3. ล้างประวัติ UI ก่อน (สำคัญมาก!)
        for widget in ranking_frame.winfo_children():
            widget.destroy()
       
        # 4. ล้าง state
        state['history_items'].clear()
        with state['lock']:
            state['last_guess_time'] = None
       
        # 5. รีเซ็ต UI elements
        entry.delete(0, 'end')
        feedback_label.configure(text="", text_color="black")
        hint_counter_label.configure(text="คำใบ้: 0/3")
        timer_label.configure(text="เวลา: 03:00")
        timer_progress.set(1.0)
        timer_progress.configure(progress_color="green")
       
        # 6. บังคับ render ทันที
        frame.update_idletasks()
       
        # 7. เริ่มเกมใหม่
        from core.game_manager import start_game as init_game
        try:
            game_info = init_game(difficulty)
            logger.info(f"[RESET] Game initialized: {game_info}")
            feedback_label.configure(text=f"พร้อมเล่น! ระดับ: {difficulty.upper()}", text_color="green")
        except Exception as e:
            logger.error(f"[RESET] Failed to start game: {e}", exc_info=True)
            feedback_label.configure(text="เกิดข้อผิดพลาด!", text_color="red")
            return
       
        # 8. เริ่ม timer และ auto hint
        start_timer()
        start_auto_hint()
       
        logger.info(f"[RESET] Complete!")

    # ================= Bind Events =================
    
    submit_btn.configure(command=submit_guess)
    hint_btn.configure(command=show_hint)
    give_up_btn.configure(command=give_up_clicked)
    entry.bind('<Return>', lambda e: submit_guess())

    # เก็บ function reset ไว้ใน frame
    frame.reset_game = reset_game
    
    # เรียกเมื่อ frame ถูกซ่อน
    def on_frame_hidden():
        stop_timer()
        logger.info("Game UI hidden, threads stopped")
    
    # เรียกเมื่อ frame ถูกแสดง (กรณีเล่นใหม่)
    def on_frame_shown():
        # ถ้ามีการเริ่มเกมใหม่จาก reset_game() จะมี timer_running = True อยู่แล้ว
        # ถ้าไม่มี ให้ตรวจสอบว่าต้องเริ่ม timer ใหม่หรือไม่
        with state['lock']:
            timer_running = state['timer_running']
        
        if not timer_running:
            # อาจจะเป็นการกลับมาหน้าเกมโดยที่เกมยังไม่จบ
            game_state = get_game_state()
            if game_state and not game_state.get('result'):
                logger.info("Resuming game on frame shown")
                # ไม่ต้องเริ่ม timer ใหม่ เพราะจะทำให้เวลารีเซ็ต
                # แค่ให้แน่ใจว่า UI แสดงผลถูกต้อง
        
        logger.info("Game UI shown")
    
    # เก็บ cleanup function ไว้ใน frame
    frame.on_hidden = on_frame_hidden
    frame.on_shown = on_frame_shown
    
    # เริ่ม auto hint
    start_auto_hint()
    
    return frame