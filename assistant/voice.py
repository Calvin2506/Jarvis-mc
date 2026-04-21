import logging

import pyttsx3
import speech_recognition as sr

logger = logging.getLogger(__name__)
_engine = None
recognizer = sr.Recognizer()
WAKE_WORD = "hey jarvis"


def _get_engine():
    global _engine
    if _engine is None:
        try:
            _engine = pyttsx3.init()
        except Exception:
            logger.error("TTS engine could not be initialized")
    return _engine


def speak(text: str) -> None:
    if not text:
        return
    engine = _get_engine()
    if engine is None:
        return
    engine.say(text)
    engine.runAndWait()


def listen() -> str:
    try:
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source)
    except OSError:
        return "Microphone is not available."
    try:
        return recognizer.recognize_whisper(audio, model="base")  # type: ignore[attr-defined]
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        return "Speech recognition service is unavailable."


def wait_for_wake_word() -> None:
    print(f"Listening for wake word '{WAKE_WORD}'...")
    while True:
        try:
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
            text = recognizer.recognize_whisper(audio, model="tiny").lower()  # type: ignore[attr-defined]
            if WAKE_WORD in text:
                print("Wake word detected.")
                return
        except sr.WaitTimeoutError:
            continue
        except Exception:
            continue
