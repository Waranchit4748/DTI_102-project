#ทำให้ข้อความเป็นตัวเล็กและตัดช่องว่างข้างหน้า-ข้างหลัง
def normalize_text(text):
    if not isinstance(text, str):
        return ""
    return text.strip().lower()

#แปลงวินาทีเป็น นาที:วินาที
def format_time(seconds):
    try:
        seconds = int(seconds)
    except (ValueError, TypeError):
        return "00:00"
    minutes = abs(seconds) // 60
    sec = abs(seconds) % 60
    s = f"{minutes:02d}:{sec:02d}"
    return "-" + s if seconds < 0 else s

#แปลงตัวเลขเป็นเปอร์เซ็นต์
def format_percentage(value):
    try:
        value = float(value)
    except (ValueError, TypeError):
        return "0%"
    return str(round(value * 100)) + "%"

#คำนวณประสิทธิภาพ
def calculate_efficiency(correct_count, total_time):
    try:
        correct_count = float(correct_count)
        total_time = float(total_time)
    except (ValueError, TypeError):
        return 0
    if total_time <= 0:
        return 0
    return correct_count / total_time

#ตรวจสอบว่าระดับอยู่ในช่วงที่กำหนด
def validate_level(level, min_level=1, max_level=10):
    try:
        level = int(level)
    except (ValueError, TypeError):
        return min_level
    if level < min_level:
        return min_level
    if level > max_level:
        return max_level
    return level

#หารเลข
def safe_divide(a, b, default=0):
    try:
        return a / b if b != 0 else default
    except (TypeError, ZeroDivisionError):
        return default

#จำกัดค่าระหว่างต่ำสุดกับสูงสุด
def clamp(value, low, high):
    try:
        value = float(value)
        low = float(low)
        high = float(high)
    except (ValueError, TypeError):
        return low
    if value < low:
        return low
    if value > high:
        return high
    return value

#ตัดข้อความถ้ายาวเกินไป
def truncate_text(text, max_length=10):
    """
    ตัดข้อความถ้ายาวเกินไป โดยรวม '...' ในความยาว max_length
    - ถ้า max_length <= 3 จะ return '...' เต็มความยาว
    - ถ้า max_length > 3 จะตัดตัวอักษรด้านหน้าให้เหลือ space สำหรับ '...'
    """
    if not isinstance(text, str):
        text = str(text)
    if len(text) <= max_length:
        return text
    if max_length <= 3:
        return '.' * max_length
    return text[:max_length - 3] + "..."

#emojiตามคะแนน
def get_feedback_emoji(score):
    try:
        score = float(score)
    except (ValueError, TypeError):
        return "💀"
    if score >= 80:
        return "😍"
    elif score >= 60:
        return "😊"
    elif score >= 40:
        return "😐"
    elif score >= 20:
        return "😢"
    else:
        return "💀"
