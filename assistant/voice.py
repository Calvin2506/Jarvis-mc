import logging
import re
from difflib import SequenceMatcher
from typing import Any, cast

import pyaudio
import pyttsx3
import speech_recognition as sr

from assistant.config import (
    MICROPHONE_DEVICE_INDEX,
    VOICE_AMBIENT_DURATION,
    VOICE_ENERGY_THRESHOLD,
    VOICE_NAME,
    VOICE_PAUSE_THRESHOLD,
    VOICE_PHRASE_TIME_LIMIT_SECONDS,
    VOICE_RATE,
    VOICE_TIMEOUT_SECONDS,
    VOICE_VOLUME,
    WAKE_PHRASE_TIME_LIMIT_SECONDS,
    WAKE_TIMEOUT_SECONDS,
    WAKE_WORD,
    WHISPER_LANGUAGE,
    WHISPER_MODEL_NAME,
    WHISPER_WAKE_MODEL_NAME,
)

logger = logging.getLogger(__name__)
_engine = None
recognizer = sr.Recognizer()
recognizer.energy_threshold = VOICE_ENERGY_THRESHOLD
recognizer.pause_threshold = VOICE_PAUSE_THRESHOLD
_VIRTUAL_DEVICES = {"blackhole", "soundflower", "virtual", "loopback"}


def _get_best_microphone() -> int | None:
    """
    Returns the best microphone index dynamically.
    Priority: .env config → macOS default input → first real input device.
    Called every time so it adapts when headphones connect or disconnect.
    """
    p = pyaudio.PyAudio()
    try:
        if MICROPHONE_DEVICE_INDEX is not None:
            try:
                info = p.get_device_info_by_index(MICROPHONE_DEVICE_INDEX)
                if int(info.get("maxInputChannels", 0)) > 0:
                    print(
                        f"Using configured microphone: {info.get('name', 'Unknown')} "
                        f"(index {MICROPHONE_DEVICE_INDEX})"
                    )
                    return MICROPHONE_DEVICE_INDEX
                print(
                    f"Configured microphone index {MICROPHONE_DEVICE_INDEX} has no input channels."
                )
            except Exception:
                print(
                    f"Configured microphone index {MICROPHONE_DEVICE_INDEX} is not available."
                )

        try:
            info = p.get_default_input_device_info()
            name = str(info.get("name", "")).lower()
            if not any(k in name for k in _VIRTUAL_DEVICES):
                print(
                    f"Using microphone: {info.get('name', 'Unknown')} (index {info['index']})"
                )
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
            print(f"Using microphone: {info.get('name', 'Unknown')} (index {i})")
            return i
    finally:
        p.terminate()

    return None


def debug_list_microphones() -> None:
    for i, name in enumerate(sr.Microphone.list_microphone_names()):
        print(f"{i}: {name}")


def _get_engine():
    global _engine
    if _engine is None:
        try:
            _engine = pyttsx3.init()
        except Exception:
            logger.error("TTS engine could not be initialized")
            return None

        voices = cast(list[Any], _engine.getProperty("voices"))
        preferred = VOICE_NAME.lower()
        voice_selected = False
        for voice in voices:
            logger.debug("Voice available: %s|%s", voice.id, voice.name)
            if preferred and (
                preferred in voice.name.lower() or preferred in voice.id.lower()
            ):
                _engine.setProperty("voice", voice.id)
                voice_selected = True
                break
        if preferred and not voice_selected:
            logger.warning(
                "Preferred voice '%s' was not found. Falling back to the system default voice.",
                VOICE_NAME,
            )
        _engine.setProperty("rate", VOICE_RATE)
        _engine.setProperty("volume", VOICE_VOLUME)
    return _engine


def speak(text: str) -> None:
    if not text:
        return
    engine = _get_engine()
    if engine is None:
        return
    spoken_text = prepare_text_for_speech(text)
    engine.say(spoken_text)
    engine.runAndWait()


def listen() -> str:
    try:
        with sr.Microphone(device_index=_get_best_microphone()) as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(
                source, duration=VOICE_AMBIENT_DURATION
            )
            audio = recognizer.listen(
                source,
                timeout=VOICE_TIMEOUT_SECONDS,
                phrase_time_limit=VOICE_PHRASE_TIME_LIMIT_SECONDS,
            )
            print("Listening... done.")
    except OSError:
        print("Microphone open failed.")
        return "Microphone is not available."
    except sr.WaitTimeoutError:
        print("No speech detected before timeout.")
        return ""
    try:
        text = recognizer.recognize_whisper(  # type: ignore[attr-defined]
            audio,
            model=WHISPER_MODEL_NAME,
            language=WHISPER_LANGUAGE,
            fp16=False,
        )
        normalized = normalize_transcript(text)
        print(f"Transcribed text: {normalized}")
        return normalized
    except sr.UnknownValueError:
        print("Audio captured, but speech was not recognized.")
        return ""
    except sr.RequestError:
        print("Whisper transcription failed.")
        return "Speech recognition service is unavailable."


def wait_for_wake_word() -> None:
    print(f"Listening for wake word '{WAKE_WORD}'...")
    while True:
        try:
            with sr.Microphone(device_index=_get_best_microphone()) as source:
                recognizer.adjust_for_ambient_noise(
                    source, duration=VOICE_AMBIENT_DURATION
                )
                audio = recognizer.listen(
                    source,
                    timeout=WAKE_TIMEOUT_SECONDS,
                    phrase_time_limit=WAKE_PHRASE_TIME_LIMIT_SECONDS,
                )
                print("Wake word audio captured.")
            text = recognizer.recognize_whisper(  # type: ignore[attr-defined]
                audio,
                model=WHISPER_WAKE_MODEL_NAME,
                language=WHISPER_LANGUAGE,
                fp16=False,
            )
            text = normalize_transcript(text)
            print(f"Wake word text: {text}")
            tokens = tokenize_wake_text(text)
            print(f"Wake word tokens: {tokens}")
            if is_wake_word_match(tokens):
                print("Wake word detected.")
                return
        except sr.WaitTimeoutError:
            print("No wake word detected.")
            continue
        except Exception as exc:
            print(f"Wake word error:{exc}")
            continue


def debug_list_voices() -> None:
    engine = _get_engine()
    if engine is None:
        print("TTS engine is not available.")
        return
    voices = cast(list[Any], engine.getProperty("voices"))
    for i, voice in enumerate(voices):
        print(f"{i}: id={voice.id}| name={voice.name}")


def prepare_text_for_speech(text: str) -> str:
    cleaned = text.strip()
    cleaned = cleaned.replace("`", "")
    cleaned = cleaned.replace("*", "")
    cleaned = cleaned.replace("_", " ")
    cleaned = cleaned.replace("%", " percent ")
    cleaned = cleaned.replace("&", " and ")
    cleaned = cleaned.replace("://", " ")
    cleaned = " ".join(cleaned.split())
    if len(cleaned) > 220:
        cleaned = cleaned[:220].rsplit(" ", 1)[0] + "."
    return cleaned


def normalize_transcript(text: object) -> str:
    if not isinstance(text, str):
        return ""
    cleaned = text.strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def tokenize_wake_text(text: str) -> list[str]:
    return re.findall(r"[a-z]+", text.lower())


def is_wake_word_match(tokens: list[str]) -> bool:
    if not tokens:
        return False

    target_tokens = tokenize_wake_text(WAKE_WORD)
    target = target_tokens[-1] if target_tokens else "jarvis"
    variants = {target, "jarvis", "jarviss", "jarvice", "jarves", "jarvus"}

    for token in tokens:
        if token in variants:
            return True
        if len(token) >= 5 and SequenceMatcher(None, token, target).ratio() >= 0.8:
            return True

    return False
