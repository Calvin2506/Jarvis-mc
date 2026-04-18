import requests

from assistant.config import (
    JARVIS_SYSTEM_PROMPT,
    OLLAMA_CHAT_URL,
    OLLAMA_MODEL_NAME,
    OLLAMA_TAGS_URL,
    OLLAMA_TIMEOUT_SECONDS,
)


def is_ollama_available() -> bool:
    try:
        response = requests.get(OLLAMA_TAGS_URL, timeout=5)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError):
        return False

    models = data.get("models", [])
    return any(model.get("name") == OLLAMA_MODEL_NAME for model in models)


def ask_llm(user_message: str, history: list[dict]) -> str:
    if not is_ollama_available():
        return (
            f"Ollama is not available, or the model '{OLLAMA_MODEL_NAME}' is not loaded. "
            "Start Ollama and make sure the model is installed."
        )

    messages = [
        {
            "role": "system",
            "content": JARVIS_SYSTEM_PROMPT,
        }
    ]

    for item in history:
        role = item.get("role")
        message = item.get("message")

        if role in {"user", "assistant"} and message:
            messages.append(
                {
                    "role": role,
                    "content": message,
                }
            )
    messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    payload = {
        "model": OLLAMA_MODEL_NAME,
        "messages": messages,
        "stream": False,
    }

    try:
        response = requests.post(
            OLLAMA_CHAT_URL,
            json=payload,
            timeout=OLLAMA_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
        data = response.json()
        message = data.get("message", {})
        content = message.get("content")

        if not isinstance(content, str) or not content.strip():
            return "I could not generate a response from Ollama."

        return content.strip()
    except requests.Timeout:
        return "Ollama took too long to respond."
    except requests.RequestException:
        return "I could not connect to your local Ollama server."
    except (AttributeError, TypeError, ValueError):
        return "Ollama returned an unexpected response."
