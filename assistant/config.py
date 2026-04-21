import os

from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_CHAT_URL = f"{OLLAMA_BASE_URL}/api/chat"
OLLAMA_TAGS_URL = f"{OLLAMA_BASE_URL}/api/tags"
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "qwen3:8b")
OLLAMA_TIMEOUT_SECONDS = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "60"))

JARVIS_SYSTEM_PROMPT = """
You are Jarvis, a local desktop AI assistant running on the user's Mac.

Behavior rules:
- Be concise, clear, and practical.
- Prefer short answers unless the user asks for detail.
- Explain technical concepts in simple language when possible.
- Do not claim to have taken actions on the computer unless the local command system actually did it.
- If the user asks for coding help, give structured, accurate guidance.
- If the request is ambiguous, ask one short clarifying question.
""".strip()
CONFIRM_ACTIONS = os.getenv("CONFIRM_ACTIONS", "true").lower() == "true"
PERSONAS = {
    "default": JARVIS_SYSTEM_PROMPT,
    "formal": """
You are Jarvis, a formal and professional desktop AI assistant running on the user's Mac.
Use precise language, avoid contractions, and maintain a professional tone all the times.
""".strip(),
    "casual": """
Your are Jarvis, a casual and friendly desktop AI assistant running on the user's Mac.
Be relaxed and conversational. Use everyday language and contractions freely
""".strip(),
    "concise": """
Your are Jarvis. Be extremely brief. Answer in one sentence or less whenever possible.
No filler words.
""".strip(),
}
_current_persona = "default"


def get_system_prompt() -> str:
    return PERSONAS.get(_current_persona, PERSONAS["default"])


def set_persona(name: str) -> bool:
    global _current_persona
    if name in PERSONAS:
        _current_persona = name
        return True
    return False
