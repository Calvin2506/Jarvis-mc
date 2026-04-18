from collections.abc import Callable


def normalize_response(response: object) -> str:
    if response is None:
        return "I could not generate a response."

    if not isinstance(response, str):
        response = str(response)

    response = response.strip()
    if not response:
        return "I could not generate a response."

    return response


def safe_execute(action: Callable[[], str]) -> str:
    try:
        return normalize_response(action())
    except Exception:
        return "Something went wrong while handling that command."
