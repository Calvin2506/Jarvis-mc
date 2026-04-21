import logging

from assistant.brain import route_command
from assistant.commands import is_dictation_active, stop_dictation, type_text_to_app
from assistant.errors import normalize_response, safe_execute
from assistant.history import add_message
from assistant.llm import is_ollama_available
from assistant.safety import is_blocked, requires_confirmation
from assistant.voice import listen, speak, wait_for_wake_word

_file_handler = logging.FileHandler("jarvis.log", encoding="utf-8")
_file_handler.setLevel(logging.DEBUG)
_file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
_console_handler = logging.StreamHandler()
_console_handler.setLevel(logging.WARNING)
_console_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))
logging.basicConfig(level=logging.DEBUG, handlers=[_file_handler, _console_handler])

VOICE_ERROR_MESSAGES = [
    "Microphone is not available.",
    "Speech recognition service is unavailable.",
]

MAX_VOICE_FAILURES = 3


def get_user_input(mode: str, failed_listens: int) -> tuple[str, str, int]:
    if mode != "voice":
        user_input = input("You: ").strip()
        if user_input.lower() == "voice":
            print("Jarvis: Switching to voice mode.")
            speak("Switching to voice mode.")
            return "", "voice", 0
        return user_input, mode, 0
    wait_for_wake_word()
    speak("Yes?")
    print("Jarvis: Yes?")
    user_input = listen()

    if user_input in VOICE_ERROR_MESSAGES:
        print(f"Jarvis: {user_input}")
        print("Jarvis: Switching to text input.")
        speak(user_input)
        return "", "text", 0

    if not user_input:
        failed_listens += 1
        print(f"Jarvis: I did not catch that.({failed_listens}/{MAX_VOICE_FAILURES})")
        speak("I did not catch that.")
        if failed_listens >= MAX_VOICE_FAILURES:
            print("Jarvis: Too many failed attempts. Switching to text input.")
            speak("Too many failed attempts. Switching to text input.")
            return "", "text", 0
        return "", mode, failed_listens
    print(f"You: {user_input}")
    return user_input.strip(), mode, 0


def confirm_action(prompt: str, mode: str) -> bool:
    if mode == "voice":
        speak(prompt)
    answer = input(f"Jarvis: {prompt} (yes/no): ").strip().lower()
    return answer in {"yes", "y"}


def main():
    print("Jarvis is online.")
    if not is_ollama_available():
        print(
            "Jarvis: Warning: Ollama is not running or the model is not loaded. LLM responses will be unavailable."
        )
    print("Type 'voice' anytime in text mode to switch back to voice mode.")
    while True:
        mode = input("Choose mode (text/voice): ").strip().lower()
        if mode in {"text", "voice"}:
            break
        print("Please choose either 'text' or 'voice'.")
    failed_listens = 0
    while True:
        user_input, mode, failed_listens = get_user_input(mode, failed_listens)
        if not user_input:
            continue
        if is_dictation_active():
            if "stop dictation" in user_input.lower():
                response = stop_dictation()
                print(f"Jarvis: {response}")
                if mode == "voice":
                    speak(response)
            else:
                response = type_text_to_app(user_input)
                print(f"Jarvis: {response}")
                if mode == "voice":
                    speak("Typed.")
            continue
        if user_input.lower() == "exit":
            response = "Jarvis is shutting down."
            print(f"Jarvis: {response}")
            if mode == "voice":
                speak(response)
            break
        command_data = route_command(user_input)
        action_name = command_data["action_name"]
        action = command_data["action"]
        validator = command_data["validator"]
        confirm_message = command_data["confirm_message"]
        should_save = False
        validation_error = validator()
        if validation_error:
            response = normalize_response(validation_error)
        elif is_blocked(action_name):
            response = "This action is blocked for safety."
        elif requires_confirmation(action_name):
            prompt = confirm_message or f"Do you want me to run '{user_input}'?"
            if not confirm_action(prompt, mode):
                response = "Action cancelled by user."
            else:
                response = safe_execute(action)
                should_save = True
        else:
            response = safe_execute(action)
            should_save = True
        response = normalize_response(response)
        if should_save:
            add_message("user", user_input)
            add_message("assistant", response)
        print(f"Jarvis: {response}")
        if mode == "voice":
            speak(response)


if __name__ == "__main__":
    main()
