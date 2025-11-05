import customtkinter as ctk
import threading
import time
import logging
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ตั้งค่าตัว logger สำหรับบันทึกเหตุการณ์
logger = logging.getLogger(__name__)

# Mock up เกม
answer = "แมว"       # คำตอบจริง
hints_used = 0        # นับจำนวนคำใบ้
max_hints = 3         # จำนวนคำใบ้สูงสุด

# ตรวจสอบว่าคำตอบของผู้เล่นตรงกับคำตอบจริงหรือไม่
def check_guess(guess):
        return guess.lower() == answer.lower()

# คืนค่าคำใบ้ตามลำดับ (สูงสุด 3 ครั้ง)
def get_hint():
    global hints_used
    hints = ["คำใบ้ที่ 1: เป็นสัตว์เลี้ยง", "คำใบ้ที่ 2: ชอบปลา", "คำใบ้ที่ 3: มีหนวด"]
    if hints_used < max_hints:
        hint = hints[hints_used]  # ดึงคำใบ้ตามจำนวนที่ใช้ไป
        hints_used += 1
        return hint
    return "ไม่มีคำใบ้แล้ว!"  # ถ้าใช้หมดแล้ว

# ฟังก์ชันวัด similarity ด้วย cosine similarity
vectorizer = CountVectorizer(token_pattern=r"(?u)\b\w+\b")  # แปลงข้อความเป็นเวกเตอร์คำ

# คำนวณเปอร์เซ็นต์ความคล้ายกันระหว่างคำตอบและคำทาย
def cosine_similarity_percent(text1, text2):
    vectors = vectorizer.fit_transform([text1, text2])
    sim = cosine_similarity(vectors[0], vectors[1])[0][0]  # ค่าความคล้าย (0-1)
    return round(sim * 100, 2)  # แปลงเป็นเปอร์เซ็นต์

# สร้าง UI หลัก
def create_game_ui(root, stack):
    frame = ctk.CTkFrame(root, fg_color="white")  # เฟรมหลักสีขาว
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
    timer_progress.set(1.0)  # เริ่มต้นเต็ม 100%
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

    # ปุ่มคำใบ้
    hint_btn = ctk.CTkButton(
        button_frame, text="คำใบ้", width=220,
        text_color="black", fg_color="yellow", hover_color="yellow",
        border_width=0, font=("Sarabun", 16)
    )
    hint_btn.grid(row=0, column=0, padx=5)

    # ปุ่มยอมแพ้
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

    # ================= Logic =================
    timer_thread = None # ตัวแปรเก็บ thread ของ timer
    timer_running = False # สถานะการนับเวลา
    guess_history = [] # เก็บประวัติการทาย

    # แปลงวินาทีเป็นรูปแบบ mm:ss
    def format_time(seconds):
        mins, secs = divmod(seconds, 60)
        return f"{mins:02d}:{secs:02d}"

    # ฟังก์ชันเริ่มจับเวลา
    def start_timer(duration=180):
        nonlocal timer_thread, timer_running
        timer_running = True
        
        # ฟังก์ชันภายใน (ทำงานใน thread แยก)
        def countdown():
            remaining = duration
            while remaining >= 0 and timer_running: 
                timer_label.configure(text=f"เวลา: {format_time(remaining)}")
                progress = remaining / duration
                color = "green" if progress >= 0.7 else "orange" if progress >= 0.4 else "red"
                # เปลี่ยนสี progress bar ตามเวลาที่เหลือ:
                # - เขียว: มากกว่า 70%
                # - ส้ม: เหลือ 40–70%
                # - แดง: เหลือต่ำกว่า 40%
    
                timer_progress.configure(progress_color=color)
                timer_progress.set(progress)
                # วนลูปขณะเวลายังไม่หมด และสถานะ timer_running ยังเป็น True
                # ถ้า stop_timer() ถูกเรียก (timer_running=False) ลูปนี้จะหยุดทันที
                
                if remaining == 0:
                    feedback_label.configure(text="หมดเวลาแล้ว!", text_color="red")
                    break
                time.sleep(1)
                # หน่วงเวลา 1 วินาที ก่อนลดเวลาลง (จำลองการนับถอยหลังจริง)
                
                remaining -= 1
                # ลดเวลาที่เหลือทีละ 1 วินาที
        
        # เริ่ม thread สำหรับจับเวลา
        timer_thread = threading.Thread(target=countdown, daemon=True)
        timer_thread.start()

    # หยุดจับเวลา
    def stop_timer():
        nonlocal timer_running
        timer_running = False

    # แสดงประวัติการทายใหม่ (เรียงตามความคล้าย)
    def refresh_history():
        for widget in ranking_frame.winfo_children():
            widget.destroy()
        sorted_history = sorted(guess_history, key=lambda x: x['similarity'], reverse=True)
        
        # แสดงแต่ละแถวในประวัติ
        for idx, item in enumerate(sorted_history, 1):
            row = ctk.CTkFrame(ranking_frame, fg_color="white")
            row.pack(fill="x", pady=3, padx=10)

            # ลำดับ
            idx_label = ctk.CTkLabel(row, text=f"{idx}.", width=30, anchor="w", text_color="black")
            idx_label.pack(side="left")

            # คำที่ทาย
            guess_label = ctk.CTkLabel(row, text=item['guess'], width=100, anchor="w", text_color="black")
            guess_label.pack(side="left")

            # แถบแสดงความคล้าย
            bar = ctk.CTkProgressBar(row, width=200)
            bar.set(item['similarity'] / 100)
            
            # สีแถบตามระดับความคล้าย
            if item['similarity'] >= 80:
                bar.configure(progress_color="green")
            elif item['similarity'] >= 50:
                bar.configure(progress_color="orange")
            else:
                bar.configure(progress_color="red")
            bar.pack(side="left", padx=10)

            # เปอร์เซ็นต์แสดงผล
            percent_label = ctk.CTkLabel(row, text=f"{item['similarity']}%", width=60)
            percent_label.pack(side="left")

    # ส่งคำตอบ
    def submit_guess():
        text = entry.get().strip()
        entry.delete(0, 'end')
        if not text:
            return
        
        # คำนวณความคล้ายระหว่างคำทายกับคำตอบจริง
        sim = cosine_similarity_percent(text, answer)
        guess_history.append({'guess': text, 'similarity': sim})
        refresh_history()

        # ตรวจว่าทายถูกหรือไม่
        if check_guess(text):
            feedback_label.configure(text="คุณทายคำถูกต้อง!", text_color="green")
            stop_timer()
        else:
            feedback_label.configure(text=f"ใกล้เคียงแล้ว {sim}%", text_color="orange")

    # คำใบ้
    def show_hint():
        hint = get_hint()
        hint_counter_label.configure(text=f"คำใบ้: {hints_used}/3")
        feedback_label.configure(text=hint, text_color="black")

    # ยอมแพ้
    def give_up_clicked():
        feedback_label.configure(text=f"ยอมแพ้แล้ว! เฉลยคือ {answer}", text_color="red")
        stop_timer()
        stack.show("Play")  # กลับไปหน้าหลัก

    # เชื่อมปุ่มกับฟังก์ชัน
    submit_btn.configure(command=submit_guess)  # ปุ่มส่งคำตอบ
    hint_btn.configure(command=show_hint)       # ปุ่มคำใบ้
    give_up_btn.configure(command=give_up_clicked)  # ปุ่มยอมแพ้

    start_timer()  # เริ่มจับเวลาเมื่อเข้าเกม
    return frame   # ส่งกลับเฟรมหลักของเกม
