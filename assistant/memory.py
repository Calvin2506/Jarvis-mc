import json
from pathlib import Path

MEMORY_FILE = Path("memory.json")


def load_memory():
    if not MEMORY_FILE.exists():
        return {}
    try:
        with MEMORY_FILE.open("r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        return {}


def save_memory(data: dict) -> None:
    with MEMORY_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=3)


def remember(key: str, value: str) -> None:
    memory = load_memory()
    memory[key] = value
    save_memory(memory)


def recall(key: str) -> str | None:
    memory = load_memory()
    return memory.get(key)
