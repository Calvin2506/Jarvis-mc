from assistant.commands import (
    normalize_website,
    repeat_text,
    say_hello,
    tell_date,
    tell_time,
)


def test_say_hello():
    assert say_hello() == "Hello. How can I assist you?"


def test_repeat_text_with_content():
    assert repeat_text("hello world") == "hello world"


def test_repeat_text_empty():
    assert "need to give" in repeat_text("").lower()


def test_normalize_website_keeps_https():
    assert normalize_website("https://github.com") == "https://github.com"


def test_normalize_website_adds_https():
    assert normalize_website("github.com") == "https://github.com"


def test_normalize_website_adds_dotcom():
    assert normalize_website("github") == "https://github.com"


def test_tell_time_format():
    result = tell_time()
    assert "AM" in result or "PM" in result


def test_tell_date_contains_year():
    result = tell_date()
    assert any(str(y) in result for y in range(2024, 2030))
