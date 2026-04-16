import subprocess
import webbrowser
from datetime import datetime
from pathlib import Path

from assistant.history import get_recent_history
from assistant.memory import recall, remember

NOTES_DIR = Path("notes")


def tell_time() -> str:
    now = datetime.now().strftime("%I:%M %p")
    return f"The current time is {now}."


def tell_date() -> str:
    today = datetime.now().strftime("%B %d, %Y")
    return f"Today's date is {today}."


def say_hello() -> str:
    return "Hello. How can I assist you?"


def repeat_text(text: str) -> str:
    if not text:
        return "You need to give me something to repeat."
    return text


def search_topic(topic: str) -> str:
    if not topic:
        return "You need to tell me what to search for."
    query = topic.replace(" ", "+")
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)
    return f"Searching the web for {topic}."


def open_website(url: str) -> str:
    if not url:
        return "You need to provide a website."

    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"

    webbrowser.open(url)
    return f"Opening {url}."


def open_app(app_name: str) -> str:
    if not app_name:
        return "You need to tell me which app to open."
    try:
        subprocess.run(["open", "-a", app_name], check=True)
        return f"Opening {app_name}."
    except subprocess.CalledProcessError:
        return f"I could not open the app '{app_name}'."


def create_note(note_text: str) -> str:
    if not note_text:
        return "You need to tell me what to write in the note."

    NOTES_DIR.mkdir(exist_ok=True)
    filename = datetime.now().strftime("note_%Y%m%d_%H%M%S.txt")
    note_path = NOTES_DIR / filename
    note_path.write_text(note_text, encoding="utf-8")

    return f"Note saved to {note_path}."


def save_name(name: str) -> str:
    if not name:
        return "You need to tell me your name."
        remember("user_name", name)
    return f"I will remember that your name is {name}."


def get_name() -> str:
    name = recall("user_name")

    if not name:
        return "I do not know your name yet."

    return f"Your name is {name}."


def show_history() -> str:
    history = get_recent_history()

    if not history:
        return "There is no conversation history yet."

    lines = []
    for item in history:
        role = item["role"].capitalize()
        message = item["message"]
        lines.append(f"{role}: {message}")

    return "\n".join(lines)


def unknown_command() -> str:
    return "I do not understand that command yet."
