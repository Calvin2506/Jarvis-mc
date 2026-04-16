from assistant.brain import process_command
from assistant.history import add_message


def main():
    print("Jarvis is online. Type 'exit' to quit.")
    while True:
        user_input = input("You:").strip()
        if user_input.lower() == "exit":
            print("Jarvis is shutting down.")
            break
        add_message("user", user_input)
        response = process_command(user_input)
        print(f"Jarvis:{response}")


if __name__ == "__main__":
    main()
