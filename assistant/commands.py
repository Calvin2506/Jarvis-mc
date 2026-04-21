import os
import re
import subprocess
import tempfile
import threading
import webbrowser
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus

import pyperclip
import requests
from simpleeval import simple_eval

from assistant.config import PERSONAS, set_persona
from assistant.history import get_recent_history
from assistant.llm import ask_llm, is_ollama_available
from assistant.memory import recall, remember

NOTES_DIR = Path("notes")


def normalize_website(url: str) -> str:
    url = url.strip()

    if not url:
        return url

    if url.startswith(("http://", "https://")):
        return url

    if "." not in url:
        url = f"{url}.com"

    return f"https://{url}"


def tell_time() -> str:
    now = datetime.now().strftime("%I:%M %p")
    return f"The current time is {now}."


def tell_date() -> str:
    today = datetime.now().strftime("%B %d, %Y")
    return f"Today's date is {today}."


def say_hello() -> str:
    return "Hello. How can I assist you?"


def repeat_text(text: str) -> str:
    text = text.strip()
    if not text:
        return "You need to give me something to repeat."
    return text


def search_topic(topic: str) -> str:
    topic = topic.strip()
    if not topic:
        return "You need to tell me what to search for."
    query = quote_plus(topic)
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)
    return f"Searching the web for {topic}."


def open_website(url: str) -> str:
    url = normalize_website(url)
    if not url:
        return "You need to provide a website."

    webbrowser.open(url)
    return f"Opening {url}."


def open_app(app_name: str) -> str:
    app_name = app_name.strip()
    if not app_name:
        return "You need to tell me which app to open."
    try:
        subprocess.run(["open", "-a", app_name], check=True)
        return f"Opening {app_name}."
    except subprocess.CalledProcessError:
        return f"I could not open the app '{app_name}'."


def create_note(note_text: str) -> str:
    note_text = note_text.strip()
    if not note_text:
        return "You need to tell me what to write in the note."

    NOTES_DIR.mkdir(exist_ok=True)
    filename = datetime.now().strftime("note_%Y%m%d_%H%M%S.txt")
    note_path = NOTES_DIR / filename
    note_path.write_text(note_text, encoding="utf-8")

    return f"Note saved to {note_path}."


def save_name(name: str) -> str:
    name = name.strip()
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


def list_notes() -> str:
    NOTES_DIR.mkdir(exist_ok=True)
    notes = sorted(NOTES_DIR.glob("*.txt"))
    if not notes:
        return "You have no saved notes."
    lines = [f"{i + 1}. {note.name}" for i, note in enumerate(notes)]
    return "Your notes:\n" + "\n".join(lines)


def read_note_aloud(identifier: str = "") -> str:
    NOTES_DIR.mkdir(exist_ok=True)
    notes = sorted(NOTES_DIR.glob("*.txt"))
    if not notes:
        return "You have no saved notes."
    if not identifier:
        note_path = notes[-1]
    elif identifier.isdigit():
        index = int(identifier) - 1
        if 0 <= index < len(notes):
            note_path = notes[index]
        else:
            return f"Note {identifier} does not exist. You have {len(notes)} note(s)."
    else:
        for note in notes:
            if identifier.lower() in note.name.lower():
                note_path = note
                break
        else:
            return f"Could not find a note matching '{identifier}'."
    return note_path.read_text(encoding="utf-8")


def delete_note(identifier: str) -> str:
    NOTES_DIR.mkdir(exist_ok=True)
    notes = sorted(NOTES_DIR.glob("*.txt"))
    if not notes:
        return "You have no saved notes."
    if identifier.isdigit():
        index = int(identifier) - 1
        if 0 <= index < len(notes):
            note_path = notes[index]
            note_path.unlink()
            return f"Deleted note: {note_path.name}."
        return f"Note {identifier} does not exist. You have {len(notes)} note(s)."
    for note in notes:
        if identifier.lower() in note.name.lower():
            note.unlink()
            return f"Deleted note: {note.name}."
    return f"Could not find a note matching '{identifier}'."


def _parse_duration(text: str) -> int:
    text = text.strip().lower()
    total = 0
    matches = re.findall(r"(\d+)\s*(hour|minute|second|hr|min|sec)s?", text)
    if not matches:
        raise ValueError(f"Could not parse duration:{text}")
    for amount_str, unit in matches:
        amount = int(amount_str)
        if unit in {"hour", "hr"}:
            total += amount * 3600
        elif unit in {"minute", "min"}:
            total += amount * 60
        elif unit in {"second", "sec"}:
            total += amount
    return total


def set_reminder(duration: str, message: str) -> str:
    try:
        seconds = _parse_duration(duration)

    except ValueError:
        return "I could not understand that duration."

    def fire():
        print(f"\nJarvis: Reminder: {message}")

    timer = threading.Timer(seconds, fire)
    timer.daemon = True
    timer.start()
    return f"Reminder set for {duration}: '{message}'."


def calculate(expression: str) -> str:
    expression = expression.strip()
    if not expression:
        return "Please provide an expression to calculate."
    try:
        result = simple_eval(expression)
        return f"The result is: {result}."
    except Exception:
        return f"Error: Could not calculate '{expression}'."


def get_weather(location: str = "") -> str:
    try:
        url = (
            f"https://wttr.in/{location}?format=3"
            if location
            else "https://wttr.in/?format=3"
        )
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text.strip()
    except requests.RequestException:
        return "Could not fetch weather. Check your internet connection."


def read_note(identifier: str) -> str:
    NOTES_DIR.mkdir(exist_ok=True)
    notes = sorted(NOTES_DIR.glob("*.txt"))
    if not notes:
        return "You have no saved notes."
    if identifier.isdigit():
        index = int(identifier) - 1
        if 0 <= index < len(notes):
            note_path = notes[index]
            content = note_path.read_text(encoding="utf-8")
            return f"Note {identifier} ({note_path.name}):\n{content}"
        return f"Note {identifier} does not exist. You have {len(notes)} note(s)."
    for note in notes:
        if identifier.lower() in note.name.lower():
            content = note.read_text(encoding="utf-8")
            return f"{note.name}:\n{content}"
    return f"Could not find a note matching '{identifier}'."


def read_clipboard() -> str:
    try:
        content = pyperclip.paste()
        return content if content else "Clipboard is empty."
    except Exception:
        return "Could not access clipboard."


def copy_to_clipboard(text: str) -> str:
    try:
        pyperclip.copy(text)
        return "Copied to clipboard."
    except Exception:
        return "Could not copy to clipboard."


def take_screenshot() -> str:
    screenshots_dir = Path("screenshots")
    screenshots_dir.mkdir(exist_ok=True)
    filename = datetime.now().strftime("screenshot_%Y%m%d_%H%M%S.png")
    path = screenshots_dir / filename
    try:
        subprocess.run(["screencapture", str(path)], check=True)
        return f"Screenshot saved to {path}."
    except subprocess.CalledProcessError:
        return "Failed to take screenshot."


def run_code(code: str) -> str:
    code = code.strip()
    if not code:
        return "No code provided."
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as f:
        f.write(code)
        tmp_path = f.name
    try:
        result = subprocess.run(
            ["python3", tmp_path],
            capture_output=True,
            text=True,
            timeout=10,
        )
        output = result.stdout.strip()
        error = result.stderr.strip()
        if error:
            return f"Error:\n{error}"
        return output or "Code ran with no output."
    except subprocess.TimeoutExpired:
        return "Code timed out after 10 seconds."
    except Exception as e:
        return f"Could not run code: {e}"
    finally:
        os.unlink(tmp_path)


def set_volume(level: str) -> str:
    level = level.strip().lower()
    if level == "mute":
        subprocess.run(["osascript", "-e", "set volume output muted true"], check=True)
        return "Volume muted."
    elif level == "unmute":
        subprocess.run(["osascript", "-e", "set volume output muted false"], check=True)
        return "Volume unmuted."
    if level.isdigit():
        vol = max(0, min(100, int(level)))
        subprocess.run(
            ["osascript", "-e", f"set volume output volume {vol}"], check=True
        )
        return f"Volume set to {vol}."
    return "Say a number between 0 and 100, 'mute', or 'unmute'."


def get_battery() -> str:
    try:
        result = subprocess.run(
            ["pmset", "-g", "batt"], capture_output=True, text=True, check=True
        )
        for line in result.stdout.splitlines():
            if "%" in line:
                parts = line.strip().split("\t")
                if len(parts) > 1:
                    info = parts[1]
                    return f"Battery: {info.split(';')[0].strip()}."
        return "Could not get battery information."
    except subprocess.SubprocessError:
        return "Error: Failed to get battery status."


def set_brightness(direction: str) -> str:
    direction = direction.strip().lower()
    if direction in {"increase", "up", "higher", "brighter"}:
        key_code = 144
        label = "increased"
    elif direction in {"decrease", "down", "lower", "dimmer"}:
        key_code = 145
        label = "decreased"
    else:
        return "Invalid direction. Use 'increase' or 'decrease'."
    try:
        subprocess.run(
            [
                "osascript",
                "-e",
                f'tell application "System Events" to key code {key_code}',
            ],
            check=True,
        )
        return f"Brightness {label}."
    except subprocess.CalledProcessError:
        return "Could not adjust brightness."


def summarize_note(identifier: str = "") -> str:
    NOTES_DIR.mkdir(exist_ok=True)
    notes = sorted(NOTES_DIR.glob("*.txt"))
    if not notes:
        return "You have no saved notes."
    if not identifier:
        note_path = notes[-1]
    elif identifier.isdigit():
        index = int(identifier) - 1
        if 0 <= index < len(notes):
            note_path = notes[index]
        else:
            return f"Note {identifier} does not exist. You have {len(notes)} notes."
    else:
        note_path = None
        for note in notes:
            if identifier.lower() in note.name.lower():
                note_path = note
                break
        if note_path is None:
            return f"Could not find a note matching '{identifier}'."
    content = note_path.read_text(encoding="utf-8")
    return ask_llm(f"Summarize the following note in 2-3 sentences:\n\n{content}", [])


def change_persona(persona: str) -> str:
    persona = persona.strip().lower()
    if set_persona(persona):
        return f"Switched to {persona} mode."
    available = ", ".join(PERSONAS.keys())
    return f"Unknown persona '{persona}'. Available: {available}."


def _run_applescript(script: str) -> str:
    result = subprocess.run(
        ["osascript", "-e", script],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _get_music_app() -> str | None:
    for app in ("Spotify", "Music", "YT Music"):
        result = subprocess.run(
            [
                "osascript",
                "-e",
                f'tell application "System Events" to (name of processes) contains "{app}"',
            ],
            capture_output=True,
            text=True,
        )
        if "true" in result.stdout.lower():
            return app
    return None


def music_control(action: str) -> str:
    app = _get_music_app()
    if not app:
        return "No music app is running.Open Spotify or Youtube Music or Apple Music first."
    action = action.strip().lower()
    if action in {"play", "resume"}:
        _run_applescript(f'tell application "{app}" to play')
        return f"Playing music on {app}."
    elif action in {"pause", "stop"}:
        _run_applescript(f'tell application "{app}" to pause')
        return "Music paused."
    elif action in {"next", "skip"}:
        _run_applescript(f'tell application "{app}" to next track')
        return "Skipped to next track."
    elif action == "previous":
        _run_applescript(f'tell application "{app}" to previous track')
        return "Going back to previous track."
    elif action == "current":
        name = _run_applescript(
            f'tell application "{app}" to get name of current track'
        )
        artist = _run_applescript(
            f'tell application "{app}" to get artist of current track'
        )
        if name:
            return f"Currently playing: {name} by {artist}."
        else:
            return "No track is currently playing."
    else:
        return f"Unknown music action '{action}'. Available: play, resume, pause, stop."


_dictation_active = False


def start_dictation() -> str:
    global _dictation_active
    _dictation_active = True
    return "Dictation mode on. Say 'stop dictation' to exit."


def stop_dictation() -> str:
    global _dictation_active
    _dictation_active = False
    return "Dictation mode off."


def is_dictation_active() -> bool:
    return _dictation_active


def type_text_to_app(text: str) -> str:
    try:
        pyperclip.copy(text)
        subprocess.run(
            [
                "osascript",
                "-e",
                'tell application "System Events" to keystroke "v" using command down',
            ],
            check=True,
        )
        return f"Typed: {text}"
    except Exception:
        return "Could not type text into the active app."


def daily_briefing() -> str:
    parts = []
    now = datetime.now()
    parts.append(
        f"Good morning! Today is {now.strftime('%A, %B %d, %Y')} "
        f"and the time is {now.strftime('%I:%M %p')}."
    )
    weather = get_weather("")
    if weather and "could not" not in weather:
        parts.append(weather)
    NOTES_DIR.mkdir(exist_ok=True)
    note_count = len(list(NOTES_DIR.glob("*.txt")))
    if note_count > 0:
        label = "note" if note_count == 1 else "notes"
        parts.append(f"You have {note_count} saved {label}.")

    if is_ollama_available():
        try:
            quote = ask_llm(
                "Give me one short motivational sentence to start the day. Maximum 15 words.",
                [],
            )
            parts.append(quote)
        except Exception:
            pass
    return " ".join(parts)


def unknown_command() -> str:
    return "I do not understand that command yet."
