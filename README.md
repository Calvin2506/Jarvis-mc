# Jarvis AI

A beginner-friendly Python desktop assistant built from scratch to learn how an AI assistant is structured internally.

## What This Project Covers

This project is focused on learning the core architecture behind a personal assistant like Jarvis:

- text input and response flow
- command parsing and routing
- modular command functions
- local automation
- persistent memory using JSON
- conversation history tracking

The goal is not just to make the assistant work, but to understand the concepts behind each feature step by step.

## Current Features

- greet the user
- tell the current time and date
- repeat custom text
- open apps on macOS
- open websites
- search the web
- create notes
- save simple user memory like name
- recall saved memory
- store recent conversation history

## Project Structure

```text
jarvis-ai/
  main.py
  README.md
  .gitignore
  assistant/
    brain.py
    commands.py
    memory.py
    history.py
    config.py
    voice.py
```

## File Responsibilities

- `main.py` runs the main Jarvis loop
- `assistant/brain.py` decides which command should run
- `assistant/commands.py` contains the actions Jarvis can perform
- `assistant/memory.py` stores simple long-term facts in JSON
- `assistant/history.py` stores recent chat messages
- `assistant/config.py` is reserved for future configuration
- `assistant/voice.py` is reserved for future voice features

## How To Run

Make sure Python 3 is installed, then run:

```bash
python3 main.py
```

## Example Commands

```text
hello
what is the time
what is the date
repeat I am learning Python
search Python classes
open website github.com
open app Calculator
note buy milk and eggs
my name is Calvin
what is my name
show history
```

## Core Concepts Implemented

### 1. Input Processing

Jarvis reads user input from the terminal and sends it into a processing function.

### 2. Command Routing

The `process_command()` function checks which command pattern matches the user input and routes it to the correct action.

### 3. Separation of Concerns

The project is split into different files so each part has a clear responsibility.

### 4. Persistent Memory

Jarvis can remember simple facts by saving data to `memory.json`.

### 5. Conversation History

Jarvis stores recent user and assistant messages in `history.json`.

## Future Improvements

- speech-to-text input
- text-to-speech responses
- reminders and scheduling
- AI model integration
- better natural language understanding
- safer and more flexible automation

## Notes

This project is being built as a learning project, so the implementation is intentionally simple and expanded step by step.
