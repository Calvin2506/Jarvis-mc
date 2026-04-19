import logging

import pyttsx3
import specch_recognition as sr

logger = logging.getLogger(__name__)
_engine = None
recognizer = sr.Recognizer()


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
        return recognizer.recognize_whisper(audio, model="base")
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        return "Speech recognition service is unavailable."
