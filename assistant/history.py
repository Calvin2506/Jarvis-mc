import json
import logging
from pathlib import Path

from assistant.llm import ask_llm, is_ollama_available

logger = logging.getLogger(__name__)

HISTORY_FILE = Path("history.json")
MAX_HISTORY_ITEMS = 20


def summarize_messages(messages: list[dict]) -> str:
    try:
        if not is_ollama_available():
            return "[Summary unavailable -Ollama if offline.]"
        text = "\n".join(f"{m['role'].capitalize()}: {m['message']}" for m in messages)
        return ask_llm(
            f"Summarize the following conversation in 2-3 sentences:\n\n{text}",
            [],
        )
    except Exception as e:
        logger.warning(f"Unexpected error while summarizing messages: {e}")
        return "[Summary unavailable -Ollama not available]"


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
    if len(history) >= MAX_HISTORY_ITEMS:
        half = MAX_HISTORY_ITEMS // 2
        summary = summarize_messages(history[:half])
        history = [
            {"role": "assistant", "message": f"[Conversation summary]: {summary}"}
        ] + history[half:]
    save_history(history)


def get_recent_history() -> list:
    return load_history()
