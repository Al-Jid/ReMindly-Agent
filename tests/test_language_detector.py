from app.services.language_detector import (
    detect_language,
    detect_language_details,
)


def test_detect_arabic():
    text = "ده شرح كامل عن الذكاء الاصطناعي والوكلاء."

    assert detect_language(text) == "arabic"


def test_detect_english():
    text = "This is a complete explanation about artificial intelligence."

    assert detect_language(text) == "english"


def test_detect_mixed_language():
    text = "الـ AI Agent بيستخدم Tools و APIs لتحقيق Goal."

    result = detect_language_details(text)

    assert result.language in {
        "arabic",
        "arabic_english",
    }

    assert result.arabic_characters > 0

    assert result.english_characters > 0


def test_unknown_language():
    assert detect_language("12345 !!!") == "unknown"
