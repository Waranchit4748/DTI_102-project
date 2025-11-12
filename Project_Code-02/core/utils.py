#ทำให้ข้อความเป็นตัวเล็กและตัดช่องว่างข้างหน้า-ข้างหลัง
def normalize_text(text):
    if not isinstance(text, str): #ตรวจสอบชนิดข้อมูล ถ้าtextไม่ใช่strก็จะเข้าเงื่อนไข
        return "" #ถ้าtextไม่ใช่strจะคืนค่าว่าง
    return text.strip().lower() #ตัดช่องว่างหน้าหลัง แต่ไม่ตัดช่องว่างภายใน  และแปลงเป็นตัวเล็ก
 
#แปลงวินาทีเป็น นาที:วินาที
def format_time(seconds):
    try:
        seconds = int(seconds) #แปลงsecondsเป็นจำนวนเต็ม
    except (ValueError, TypeError): #ถ้าเป็นstrหรือค่าที่ไม่สามารถแปลงได้
        return "00:00" #คืนค่า 00:00
    minutes = abs(seconds) // 60 #ใช้absเพื่อรองรับค่าลบ
    sec = abs(seconds) % 60
    s = f"{minutes:02d}:{sec:02d}" #รูปแบบสตริง 02dเติมศูนย์ข้างหน้าให้มี2หลัก
    return "-" + s if seconds < 0 else s #ถ้าสตริงเดิมติดลบจะเติมค่าลบ ถ้าไม่ติดลบจะคืนค่าปกติ
 
#แปลงตัวเลขเป็นเปอร์เซ็นต์
def format_percentage(value):
    try:
        value = float(value) #แปลงvalueเป็นทศนิยม
    except (ValueError, TypeError): #ถ้าเป็นstrหรือค่าที่ไม่สามารถแปลงได้
        return "0%" #คืนค่า 0%
    return str(round(value * 100)) + "%" #คืนค่าที่คำนวณเป็นเปอร์เซ็นต์ ปัดเศษเป็นจำนวนเต็ม
 
#คำนวณประสิทธิภาพ
def calculate_efficiency(correct_count, total_time):
    try:
        correct_count = float(correct_count)
        total_time = float(total_time)
    except (ValueError, TypeError):
        return 0
    if total_time <= 0: #ตรวจสอบเวลาทั้งหมด ถ้าเป็น0หรือลบ
        return 0 #คืนค่า 0
    return correct_count / total_time #คืนค่าที่คำนวณออกมาเป็นทศนิยม
 
#ตรวจสอบว่าระดับอยู่ในช่วงที่กำหนด
def validate_level(level, min_level=1, max_level=10): #รับตัวแปรlevel กำหนด min = 1 max = 10
    try:
        level = int(level) #แปลงlevelเป็นจำนวนเต็ม
    except (ValueError, TypeError): #ถ้าเป็นstrหรือค่าที่ไม่สามารถแปลงได้
        return min_level 
    if level < min_level:
        return min_level
    if level > max_level:
        return max_level
    return level
 
#หารเลข
def safe_divide(a, b, default=0):
    try:
        return a / b if b != 0 else default #ถ้า b ไม่เท่ากับ0 จะนำไปหาร ถ้าเท่ากับ0คืนค่าdefault
    except (TypeError, ZeroDivisionError): #ถ้าเป็นnoneหรือค่าที่ไม่สามารถแปลงได้
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