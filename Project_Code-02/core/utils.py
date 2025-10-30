def normalize_text(text: str) -> str:
    if not isinstance(text, str):
        return ""
    return text.strip().lower()

def format_time(seconds: int) -> str:
    is_negative = seconds < 0
    abs_seconds = abs(seconds)
    minutes = abs_seconds // 60
    sec = abs_seconds % 60
    time_str = f"{minutes:02d}:{sec:02d}"
    return f"-{time_str}" if is_negative else time_str

def format_percentage(value: float) -> str:
    percentage = round(value * 100)
    return f"{percentage}%"

def calculate_efficiency(correct_count: int, total_time: float) -> float:
    if total_time <= 0:
        return 0.0
    return correct_count / total_time

def validate_level(level: int, min_level: int = 1, max_level: int = 10) -> int:
    if level < min_level:
        return min_level
    if level > max_level:
        return max_level
    return level

def safe_divide(a: float, b: float, default: float = 0.0) -> float:
    return a / b if b != 0 else default

def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(value, high))

def truncate_text(text: str, max_length: int = 10) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
