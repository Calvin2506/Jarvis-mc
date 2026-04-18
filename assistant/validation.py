def validate_non_empty(value: str, field_name: str) -> str | None:
    if not value.strip():
        return f"{field_name} cannot be empty."
    return None


def validate_open_website(url: str) -> str | None:
    return validate_non_empty(url, "Website URL")


def validate_open_app(app_name: str) -> str | None:
    return validate_non_empty(app_name, "App name")


def validate_search_query(query: str) -> str | None:
    return validate_non_empty(query, "Search query")


def validate_note(note_text: str) -> str | None:
    return validate_non_empty(note_text, "Note text")


def validate_name(name: str) -> str | None:
    return validate_non_empty(name, "Name")


def no_validation() -> str | None:
    return None
