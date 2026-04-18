import pyttsx3
import speech_recognition as sr

engine = pyttsx3.init()
recognizer = sr.Recognizer()


def speak(text: str) -> None:
    if not text:
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
        return recognizer.recognize_google(audio)  # type:ignore[attr-defined]
    except sr.UnknownValueError:
        return ""
    except sr.RequestError:
        return "Speech recognition service is unavailable."
