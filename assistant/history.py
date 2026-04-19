import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

HISTORY_FILE = Path("history.json")
MAX_HISTORY_ITEMS = 20


def load_history() -> list:
    if not HISTORY_FILE.exists():
        return []

    try:
        with HISTORY_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return []


def save_history(history: list) -> None:
    try:
        with HISTORY_FILE.open("w", encoding="utf-8") as file:
            json.dump(history, file, indent=2)
    except OSError:
        logger.warning("Unexpected error while saving history")


def add_message(role: str, message: str) -> None:
    history = load_history()

    history.append({"role": role, "message": message})

    history = history[-MAX_HISTORY_ITEMS:]
    save_history(history)


def get_recent_history() -> list:
    return load_history()
