import os

from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_CHAT_URL = f"{OLLAMA_BASE_URL}/api/chat"
OLLAMA_TAGS_URL = f"{OLLAMA_BASE_URL}/api/tags"
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "qwen3:8b")
OLLAMA_TIMEOUT_SECONDS = int(os.getenv("OLLAMA_TIMEOUT_SECONDS", "60"))
VOICE_NAME = os.getenv("VOICE_NAME", "")
VOICE_RATE = int(os.getenv("VOICE_RATE", "100"))
VOICE_VOLUME = float(os.getenv("VOICE_VOLUME", "1.0"))
WHISPER_MODEL_NAME = os.getenv("WHISPER_MODEL_NAME", "base")
WHISPER_WAKE_MODEL_NAME = os.getenv("WHISPER_WAKE_MODEL_NAME", "tiny")
WHISPER_LANGUAGE = os.getenv("WHISPER_LANGUAGE", "en")
VOICE_ENERGY_THRESHOLD = int(os.getenv("VOICE_ENERGY_THRESHOLD", "300"))
VOICE_PAUSE_THRESHOLD = float(os.getenv("VOICE_PAUSE_THRESHOLD", "0.8"))
VOICE_AMBIENT_DURATION = float(os.getenv("VOICE_AMBIENT_DURATION", "0.8"))
VOICE_TIMEOUT_SECONDS = int(os.getenv("VOICE_TIMEOUT_SECONDS", "8"))
VOICE_PHRASE_TIME_LIMIT_SECONDS = int(os.getenv("VOICE_PHRASE_TIME_LIMIT_SECONDS", "12"))
WAKE_WORD = os.getenv("WAKE_WORD", "hey jarvis")
WAKE_TIMEOUT_SECONDS = int(os.getenv("WAKE_TIMEOUT_SECONDS", "6"))
WAKE_PHRASE_TIME_LIMIT_SECONDS = int(os.getenv("WAKE_PHRASE_TIME_LIMIT_SECONDS", "4"))

_mic_index = os.getenv("MICROPHONE_DEVICE_INDEX")
MICROPHONE_DEVICE_INDEX: int | None = (
    int(_mic_index) if _mic_index is not None else None
)

JARVIS_SYSTEM_PROMPT = """
You are Jarvis, a precise voice assistant running on the user's Mac.

Behavior rules:
- Speak in short, polished sentences.
- Sound calm, confident, and discreet.
- Avoid slang, emojis, markdown, and bullet points unless asked.
- Keep most spoken replies under two sentences.
- Be concise, clear, and practical.
- Do not claim to have taken actions on the computer unless the local command system actually did it.
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
