import re
from collections.abc import Callable

from assistant.commands import (
    calculate,
    change_persona,
    create_note,
    daily_briefing,
    delete_note,
    get_battery,
    get_name,
    get_weather,
    list_notes,
    music_control,
    open_app,
    open_website,
    read_note_aloud,
    repeat_text,
    save_name,
    say_hello,
    search_topic,
    set_brightness,
    set_reminder,
    set_volume,
    show_history,
    start_dictation,
    stop_dictation,
    summarize_note,
    tell_date,
    tell_time,
)
from assistant.history import get_recent_history
from assistant.llm import ask_llm
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

_reminder_re = re.compile(r"remind(?:\s+me)?\s+in\s+(.+?)\s+to\s+(.+)", re.IGNORECASE)


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

    if lowered_command == "create note" or lowered_command.startswith("create note "):
        note_text = cleaned_command[4:].strip()
        return make_command(
            "create_note",
            lambda: create_note(note_text),
            validator=lambda: validate_note(note_text),
            confirm_message="Do you want me to save this note?",
        )

    if lowered_command == "show history":
        return make_command("show_history", lambda: show_history())

    if lowered_command == "list notes":
        return make_command("list_notes", lambda: list_notes())

    if lowered_command == "read note" or lowered_command.startswith("read note "):
        identifier = cleaned_command[10:].strip()
        if len(lowered_command) > 10:
            identifier = cleaned_command[10:].strip()
        else:
            identifier = ""
        return make_command("read_note_aloud", lambda: read_note_aloud(identifier))

    if lowered_command == "delete note" or lowered_command.startswith("delete note "):
        identifier = cleaned_command[11:].strip()
        return make_command(
            "delete_note",
            lambda: delete_note(identifier),
            validator=lambda: validate_note_identifier(identifier),
            confirm_message=f"Do you want me to delete note '{identifier}'?",
        )
    reminder_match = _reminder_re.match(cleaned_command)
    if reminder_match:
        duration = reminder_match.group(1).strip()
        message = reminder_match.group(2).strip()
        return make_command("set_reminder", lambda: set_reminder(duration, message))

    if lowered_command.startswith("calculate") or lowered_command.startswith("calc "):
        expr = cleaned_command.split(" ", 1)[1].strip()
        return make_command(
            "calculate",
            lambda: calculate(expr),
            validator=lambda: validate_expression(expr),
        )
    if "weather" in lowered_command:
        location = ""
        if "in" in lowered_command:
            location = cleaned_command.split(" in ", 1)[1].strip()
        elif lowered_command.startswith("weather"):
            location = cleaned_command[8:].strip()
        return make_command("get_weather", lambda: get_weather(location))

    if lowered_command == "mute":
        return make_command("set_volume", lambda: set_volume("mute"))

    if lowered_command == "unmute":
        return make_command("set_volume", lambda: set_volume("unmute"))

    if lowered_command.startswith("set volume ") or lowered_command.startswith(
        "volume "
    ):
        level = cleaned_command.split()[-1]
        return make_command("set_volume", lambda: set_volume(level))
    if "battery" in lowered_command:
        return make_command("get_battery", lambda: get_battery())

    if "brightness" in lowered_command:
        if any(w in lowered_command for w in {"increase", "up", "higher", "brighter"}):
            direction = "increase"
        else:
            direction = "decrease"
        return make_command("set_brightness", lambda: set_brightness(direction))
    if lowered_command == "summarize note" or lowered_command.startswith(
        "summarize note "
    ):
        identifier = cleaned_command[14:].strip()
        return make_command("summarize_note", lambda: summarize_note(identifier))

    if lowered_command.startswith("change persona ") or lowered_command.startswith(
        "persona"
    ):
        prefix = (
            "set persona" if lowered_command.startswith("set persona") else "persona"
        )
        persona = lowered_command[len(prefix) :].strip()
        return make_command("set_persona", lambda: change_persona(persona))
    BRIEFING_TRIGGERS = {
        "good morning",
        "daily briefing",
        "briefing",
        "daily summary",
        "morning summary",
    }
    if lowered_command in BRIEFING_TRIGGERS:
        return make_command("daily_briefing", lambda: daily_briefing())
    if (
        "music" in lowered_command
        or "song" in lowered_command
        or "track" in lowered_command
        or "now playing" in lowered_command
        or lowered_command in {"play", "pause", "skip", "resume"}
    ):
        if any(w in lowered_command for w in {"next", "skip"}):
            action = "next"
        elif "previous" in lowered_command or "back" in lowered_command:
            action = "previous"
        elif "pause" in lowered_command or "stop music" in lowered_command:
            action = "pause"
        elif "play" in lowered_command or "resume" or "play music" in lowered_command:
            action = "play"
        elif any(w in lowered_command for w in {"current", "what", "now playing"}):
            action = "current"
        else:
            action = lowered_command
        return make_command("music_control", lambda: music_control(action))

    if "start dication" in lowered_command or lowered_command == "dictation on":
        return make_command("start_dictation", lambda: start_dictation())

    if "stop dictation" in lowered_command or lowered_command == "dictation off":
        return make_command("stop_dictation", lambda: stop_dictation())

    history = get_recent_history()

    return make_command("ask_llm", lambda: ask_llm(cleaned_command, history))
