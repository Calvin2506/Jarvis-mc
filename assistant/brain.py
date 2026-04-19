from collections.abc import Callable

from assistant.commands import (
    create_note,
    get_name,
    open_app,
    open_website,
    repeat_text,
    save_name,
    say_hello,
    search_topic,
    show_history,
    tell_date,
    tell_time,
)
from assistant.history import get_recent_history
from assistant.llm import ask_llm
from assistant.validation import (
    no_validation,
    validate_name,
    validate_note,
    validate_open_app,
    validate_open_website,
    validate_search_query,
)


def make_command(
    action_name: str,
    action: Callable[[], str],
    validator: Callable[[], str | None] = no_validation,
    confirm_message: str | None = None,
) -> dict:
    return {
        "action_name": action_name,
        "action": action,
        "validator": validator,
        "confirm_message": confirm_message,
    }


def route_command(command: str) -> dict:
    cleaned_command = command.strip()
    lowered_command = cleaned_command.lower()

    if lowered_command in {"hello", "hi", "hey"}:
        return make_command("say_hello", lambda: say_hello())

    if "time" in lowered_command:
        return make_command("tell_time", lambda: tell_time())

    if "date" in lowered_command:
        return make_command("tell_date", lambda: tell_date())

    if lowered_command.startswith("repeat "):
        text = cleaned_command[7:].strip()
        return make_command("repeat_text", lambda: repeat_text(text))

    if lowered_command == "search" or lowered_command.startswith("search "):
        topic = cleaned_command[6:].strip()
        return make_command(
            "search_topic",
            lambda: search_topic(topic),
            validator=lambda: validate_search_query(topic),
            confirm_message=f"Do you want me to search the web for '{topic}'?",
        )

    if lowered_command == "open app" or lowered_command.startswith("open app "):
        app_name = cleaned_command[8:].strip()
        return make_command(
            "open_app",
            lambda: open_app(app_name),
            validator=lambda: validate_open_app(app_name),
            confirm_message=f"Do you want me to open the app '{app_name}'?",
        )

    if lowered_command == "open website" or lowered_command.startswith("open website "):
        website = cleaned_command[12:].strip()
        return make_command(
            "open_website",
            lambda: open_website(website),
            validator=lambda: validate_open_website(website),
            confirm_message=f"Do you want me to open the website '{website}'?",
        )

    if lowered_command == "note" or lowered_command.startswith("note "):
        note_text = cleaned_command[4:].strip()
        return make_command(
            "create_note",
            lambda: create_note(note_text),
            validator=lambda: validate_note(note_text),
            confirm_message="Do you want me to save this note?",
        )

    if lowered_command == "my name is" or lowered_command.startswith("my name is "):
        name = cleaned_command[10:].strip()
        return make_command(
            "save_name",
            lambda: save_name(name),
            validator=lambda: validate_name(name),
        )

    if lowered_command == "what is my name":
        return make_command("get_name", lambda: get_name())

    if lowered_command == "show history":
        return make_command("show_history", lambda: show_history())

    history = get_recent_history()

    return make_command("ask_llm", lambda: ask_llm(cleaned_command, history))
