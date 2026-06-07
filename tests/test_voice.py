from assistant.voice import (
    is_wake_word_match,
    normalize_transcript,
    prepare_text_for_speech,
    tokenize_wake_text,
)


def test_normalize_transcript_strips_extra_spacing():
    assert normalize_transcript("  open   safari\nnow  ") == "open safari now"


def test_tokenize_wake_text_removes_punctuation():
    assert tokenize_wake_text("Hey, Jarvis!") == ["hey", "jarvis"]


def test_wake_word_matches_common_whisper_variants():
    assert is_wake_word_match(["hey", "jarvice"])
    assert is_wake_word_match(["jarviss"])


def test_prepare_text_for_speech_cleans_markdown_and_symbols():
    result = prepare_text_for_speech("**CPU** is 75% & https://example.com")
    assert "*" not in result
    assert "75 percent" in result
    assert " and " in result
