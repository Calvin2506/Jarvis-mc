from assistant.validation import (
    no_validation,
    validate_expression,
    validate_name,
    validate_note,
    validate_note_identifier,
    validate_open_app,
    validate_open_website,
    validate_search_query,
)


def test_all_validators_pass_on_non_empty():
    assert validate_open_website("github.com") is None
    assert validate_open_app("Safari") is None
    assert validate_search_query("python") is None
    assert validate_note("hello") is None
    assert validate_name("Calvin") is None
    assert validate_note_identifier("1") is None
    assert validate_expression("2 + 2") is None


def test_all_validators_fail_on_empty():
    assert validate_open_website("") is not None
    assert validate_open_app("") is not None
    assert validate_search_query("") is not None
    assert validate_note("") is not None
    assert validate_name("") is not None
    assert validate_note_identifier("") is not None
    assert validate_expression("") is not None


def test_no_validation_always_passes():
    assert no_validation() is None
