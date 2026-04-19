import logging
from collections.abc import Callable

logger = logging.getLogger(__name__)


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
        logger.exception("Unexpected error while executing action")
        return "Something went wrong while handling that command."
