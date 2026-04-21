from assistant.config import CONFIRM_ACTIONS

SAFE = "safe"
CONFIRM = "confirm"
BLOCKED = "blocked"
COMMAND_POLICIES = {
    "tell_time": SAFE,
    "tell_date": SAFE,
    "say_hello": SAFE,
    "repeat_text": SAFE,
    "get_name": SAFE,
    "save_name": SAFE,
    "show_history": SAFE,
    "ask_llm": SAFE,
    "search_topic": CONFIRM,
    "open_app": CONFIRM,
    "open_website": CONFIRM,
    "create_note": CONFIRM,
    "list_notes": SAFE,
    "read_note_aloud": SAFE,
    "delete_note": CONFIRM,
    "set_reminder": SAFE,
    "calculator": SAFE,
    "get_weather": SAFE,
    "set_volume": SAFE,
    "get_battery": SAFE,
    "set_brightness": SAFE,
    "summarize_note": SAFE,
    "change_persona": SAFE,
    "music_control": SAFE,
    "start_dictation": SAFE,
    "daily_briefing": SAFE,
}


def get_policy(action_name: str) -> str:
    return COMMAND_POLICIES.get(action_name, BLOCKED)


ALWAYS_CONFIRM = {"delete_note"}


def requires_confirmation(action_name: str) -> bool:
    if action_name in ALWAYS_CONFIRM:
        return True
    if not CONFIRM_ACTIONS:
        return False
    return get_policy(action_name) == CONFIRM


def is_blocked(action_name: str) -> bool:
    return get_policy(action_name) == BLOCKED
