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
}


def get_policy(action_name: str) -> str:
    return COMMAND_POLICIES.get(action_name, BLOCKED)


def requires_confirmation(action_name: str) -> bool:
    return get_policy(action_name) == BLOCKED


def is_blocked(action_name: str) -> bool:
    return get_policy(action_name) == BLOCKED
