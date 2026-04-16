from assistant.brain import route_command
from assistant.history import add_message
from assistant.safety import is_blocked, requires_confirmation
from assistant.voice import listen, speak

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


def confirm_action(command: str, mode: str) -> bool:
    prompt = f"Jarvis: This action needs confirmation: '{command}'. Proceed? (yes/no)"
    if mode == "voice":
        speak("This action needs confirmation. Proceed?")
    answer = input(prompt).strip().lower()
    return answer in {"yes", "y"}


def main():
    print("Jarvis is online.")
    print("Type 'voice' anytime in text mode to switch back to voice mode.")
    mode = input("Choose mode (text/voice): ").strip().lower()
    failed_listens = 0
    while True:
        user_input, mode, failed_listens = get_user_input(mode, failed_listens)
        if not user_input:
            continue
        if user_input.lower() == "exit":
            response = "Jarvis is shutting down."
            print(f"Jarvis:{response}")
            if mode == "voice":
                speak(response)
            break
        action_name, action = route_command(user_input)
        if is_blocked(action_name):
            response = "This action is blocked for safety."
        elif requires_confirmation(action_name) and not confirm_action(
            user_input, mode
        ):
            response = "Action cancelled by user."
        else:
            response = action()
        add_message("user", user_input)
        add_message("assistant", response)
        print(f"Jarvis: {response}")
        if mode == "voice":
            speak(response)


if __name__ == "__main__":
    main()
