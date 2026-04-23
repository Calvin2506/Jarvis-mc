import logging

import pyaudio
import pyttsx3
import speech_recognition as sr

from assistant.config import MICROPHONE_DEVICE_INDEX

logger = logging.getLogger(__name__)
_engine = None
recognizer = sr.Recognizer()
WAKE_WORD = "hey jarvis"
_VIRTUAL_DEVICES = {"blackhole", "soundflower", "virtual", "loopback"}


def _get_best_microphone() -> int | None:
    """
    Returns the best microphone index dynamically.
    Priority: .env config → macOS default input → first real input device.
    Called every time so it adapts when headphones connect or disconnect.
    """
    if MICROPHONE_DEVICE_INDEX is not None:
        return MICROPHONE_DEVICE_INDEX

    p = pyaudio.PyAudio()
    try:
        try:
            info = p.get_default_input_device_info()
            name = str(info.get("name", "")).lower()
            if not any(k in name for k in _VIRTUAL_DEVICES):
                return int(info["index"])
        except Exception:
            pass

        for i in range(p.get_device_count()):
            info = p.get_device_info_by_index(i)
            if int(info.get("maxInputChannels", 0)) <= 0:
                continue
            name = str(info.get("name", "")).lower()
            if any(k in name for k in _VIRTUAL_DEVICES):
                continue
            return i
    finally:
        p.terminate()

    return None


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
        with sr.Microphone(device_index=_get_best_microphone()) as source:
            print("Listening...")
            audio = recognizer.listen(source, timeout=8, phrase_time_limit=10)
    except OSError:
        return "Microphone is not available."
    except sr.WaitTimeoutError:
        return ""
    try:
        return recognizer.recognize_whisper(audio, model="base", language="english")  # type: ignore[attr-defined]  # noqa: E501
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        return "Speech recognition service is unavailable."


def wait_for_wake_word() -> None:
    print(f"Listening for wake word '{WAKE_WORD}'...")
    while True:
        try:
            with sr.Microphone(device_index=_get_best_microphone()) as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=3)
            text = recognizer.recognize_whisper(  # type: ignore[attr-defined]
                audio, model="tiny", language="english"
            ).lower()
            if "jarvis" in text:
                print("Wake word detected.")
                return
        except sr.WaitTimeoutError:
            continue
        except Exception:
            continue
