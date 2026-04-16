from assistant.commands import (
    create_note,
    get_color,
    get_name,
    open_app,
    open_website,
    play_song,
    repeat_text,
    save_color,
    save_name,
    say_hello,
    search_topic,
    set_reminder,
    tell_date,
    tell_time,
    unknown_command,
)


def process_command(command: str) -> str:
    cleaned_command = command.strip()
    lowered_command = cleaned_command.lower()
    if cleaned_command in {"hello", "hi"}:
        return say_hello()
    if cleaned_command.startswith("my name is "):
        name = cleaned_command[11:].strip()
        return save_name(name)
    if "time" in cleaned_command:
        return tell_time()
    if "date" in cleaned_command:
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
    if lowered_command.startswith("reminder "):
        text = cleaned_command.removeprefix("reminder ").strip()
        return set_reminder(text)
    if lowered_command.startswith("play "):
        song = cleaned_command.removeprefix("play ").strip()
        return play_song(song)
    if cleaned_command == "what is my name":
        return get_name()
    if lowered_command.startswith("my favorite color is "):
        color = cleaned_command[20:].strip()
        return save_color(color)
    if cleaned_command == "what is my favorite color":
        return get_color()
    return unknown_command()
