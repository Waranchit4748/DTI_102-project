import pytest
from core.utils import (
    normalize_text,
    format_time,
    format_percentage,
    calculate_efficiency,
    validate_level,
    safe_divide,
    clamp,
    truncate_text
)

#normalize_text
@pytest.mark.parametrize("input_text,expected", [
    ("  Hello World  ", "hello world"),
    ("MULTIPLE   spaces", "multiple   spaces"),
    ("Already clean", "already clean"),
    ("", ""),
    (123, ""),
])
def test_normalize_text(input_text, expected):
    assert normalize_text(input_text) == expected

#format_time
@pytest.mark.parametrize("seconds,expected", [
    (0, "00:00"),
    (65, "01:05"),
    (3599, "59:59"),
    (-10, "-00:10"),
    (-65, "-01:05"),
])
def test_format_time(seconds, expected):
    assert format_time(seconds) == expected

#format_percentage
@pytest.mark.parametrize("value,expected", [
    (0.5, "50%"),
    (1.0, "100%"),
    (0.1234, "12%"),
    (0, "0%"),
])
def test_format_percentage(value, expected):
    assert format_percentage(value) == expected

#calculate_efficiency
@pytest.mark.parametrize("correct,total,expected", [
    (5, 10, 0.5),
    (0, 5, 0.0),
    (3, 0, 0.0),
    (7, -5, 0.0),
])
def test_calculate_efficiency(correct, total, expected):
    assert calculate_efficiency(correct, total) == expected

#validate_level
@pytest.mark.parametrize("level,min_level,max_level,expected", [
    (5, 1, 10, 5),
    (0, 1, 10, 1),
    (11, 1, 10, 10),
])
def test_validate_level(level, min_level, max_level, expected):
    assert validate_level(level, min_level, max_level) == expected

#safe_divide
@pytest.mark.parametrize("a,b,default,expected", [
    (10, 2, 0, 5),
    (5, 0, 0, 0),
    (5, 0, 1.5, 1.5),
])
def test_safe_divide(a, b, default, expected):
    assert safe_divide(a, b, default) == expected

#clamp
@pytest.mark.parametrize("value,low,high,expected", [
    (5, 0, 10, 5),
    (-1, 0, 10, 0),
    (15, 0, 10, 10),
])
def test_clamp(value, low, high, expected):
    assert clamp(value, low, high) == expected

#truncate_text
@pytest.mark.parametrize("text,max_length,expected", [
    ("Hello World", 20, "Hello World"),
    ("Hello World", 5, "He..."),
    ("Short", 10, "Short"),
    ("ExactLength", 11, "ExactLength"),
])
def test_truncate_text(text, max_length, expected):
    assert truncate_text(text, max_length) == expected