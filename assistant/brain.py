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
    unknown_command,
)


def process_command(command: str) -> str:
    cleaned_command = command.strip()
    lowered_command = cleaned_command.lower()

    if lowered_command in {"hello", "hi"}:
        return say_hello()
    if "time" in lowered_command:
        return tell_time()
    if "date" in lowered_command:
        return tell_date()
    if lowered_command.startswith("repeat "):
        text = cleaned_command[7:].strip()
        return repeat_text(text)
    if lowered_command.startswith("search "):
        topic = cleaned_command[7:].strip()
        return search_topic(topic)
    if lowered_command.startswith("open app "):
        app_name = cleaned_command[9:].strip()
        return open_app(app_name)
    if lowered_command.startswith("open website "):
        website = cleaned_command[13:].strip()
        return open_website(website)
    if lowered_command.startswith("note "):
        note_text = cleaned_command[5:].strip()
        return create_note(note_text)
    if lowered_command.startswith("my name is "):
        name = cleaned_command[11:].strip()
        return save_name(name)
    if lowered_command == "what is my name":
        return get_name()
    if lowered_command == "show history":
        return show_history()

    return unknown_command()
