import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.utils import (
    normalize_text,
    format_time,
    format_percentage,
    calculate_efficiency,
    validate_level,
    safe_divide,
    clamp,
    truncate_text,
    get_feedback_emoji
)

# ฟังก์ชันช่วยแสดงผล
def print_result(name, passed):
    print(f"{name}: {'✅' if passed else '❌'}")

# -------------------------------
# 1. Test normalize_text()
# -------------------------------
def test_normalize_text():
    print_result("normalize_text - basic", normalize_text(" Hello ") == "hello")
    print_result("normalize_text - not string", normalize_text(123) == "")
    print_result("normalize_text - empty", normalize_text("  ") == "")

# -------------------------------
# 2. Test format_time()
# -------------------------------
def test_format_time():
    print_result("format_time - normal", format_time(125) == "02:05")
    print_result("format_time - negative", format_time(-90) == "-01:30")
    print_result("format_time - invalid", format_time("abc") == "00:00")

# -------------------------------
# 3. Test format_percentage()
# -------------------------------
def test_format_percentage():
    print_result("format_percentage - 0.5", format_percentage(0.5) == "50%")
    print_result("format_percentage - 1.23", format_percentage(1.23) == "123%")
    print_result("format_percentage - invalid", format_percentage("abc") == "0%")

# -------------------------------
# 4. Test calculate_efficiency()
# -------------------------------
def test_calculate_efficiency():
    print_result("calculate_efficiency - normal", calculate_efficiency(10, 5) == 2)
    print_result("calculate_efficiency - zero time", calculate_efficiency(5, 0) == 0)
    print_result("calculate_efficiency - invalid", calculate_efficiency("a", 10) == 0)

# -------------------------------
# 5. Test validate_level()
# -------------------------------
def test_validate_level():
    print_result("validate_level - normal", validate_level(5) == 5)
    print_result("validate_level - below min", validate_level(0) == 1)
    print_result("validate_level - above max", validate_level(15) == 10)
    print_result("validate_level - invalid", validate_level("abc") == 1)

# -------------------------------
# 6. Test safe_divide()
# -------------------------------
def test_safe_divide():
    print_result("safe_divide - normal", safe_divide(10, 2) == 5)
    print_result("safe_divide - divide by zero", safe_divide(5, 0) == 0)
    print_result("safe_divide - invalid", safe_divide("a", 2) == 0)

# -------------------------------
# 7. Test clamp()
# -------------------------------
def test_clamp():
    print_result("clamp - normal", clamp(5, 1, 10) == 5)
    print_result("clamp - below low", clamp(-2, 1, 10) == 1)
    print_result("clamp - above high", clamp(15, 1, 10) == 10)
    print_result("clamp - invalid", clamp("abc", 1, 10) == 1)

# -------------------------------
# 8. Test truncate_text()
# -------------------------------
def test_truncate_text():
    print_result("truncate_text - short", truncate_text("Hi", 5) == "Hi")
    print_result("truncate_text - long", truncate_text("HelloWorld", 5) == "He...")
    print_result("truncate_text - tiny max", truncate_text("Hello", 3) == "...")
    print_result("truncate_text - not str", truncate_text(12345, 6) == "12345")


# -------------------------------
# 9. Test get_feedback_emoji()
# -------------------------------
def test_get_feedback_emoji():
    print_result("emoji - excellent", get_feedback_emoji(95) == "😍")
    print_result("emoji - good", get_feedback_emoji(70) == "😊")
    print_result("emoji - average", get_feedback_emoji(50) == "😐")
    print_result("emoji - low", get_feedback_emoji(30) == "😢")
    print_result("emoji - bad", get_feedback_emoji(10) == "💀")

# -------------------------------
# Run all tests
# -------------------------------
if __name__ == "__main__":
    print("=== Running Utility Function Tests ===")
    test_normalize_text()
    test_format_time()
    test_format_percentage()
    test_calculate_efficiency()
    test_validate_level()
    test_safe_divide()
    test_clamp()
    test_truncate_text()
    test_get_feedback_emoji()
