# Jarvis AI 🤖

A privacy-first, local desktop AI assistant for macOS — inspired by Iron Man's Jarvis. Powered by [Ollama](https://ollama.com) for fully offline LLM responses, with voice and text interaction support.

---

## ✨ Features

### 🎙️ Voice & Text Modes
- Switch between **text** and **voice** mode at startup
- Wake word detection — say **"Hey Jarvis"** to activate in voice mode
- Auto-detects microphone (adapts when headphones connect/disconnect)
- Local speech-to-text via **OpenAI Whisper** (no cloud, no data sent)
- Text-to-speech responses via **pyttsx3**

### 🧠 LLM Integration
- Powered by **Ollama** running locally — fully offline
- Falls back to Ollama for any unrecognised command
- Configurable model via `.env` (default: `qwen3:8b`)
- Persona switching — formal, casual, concise modes
- Multi-turn memory summarisation when history limit is reached

### 📝 Notes
- Create, list, read, delete notes
- Read notes aloud
- Summarise notes using Ollama

### 🗓️ Productivity
- Reminders and timers (`"remind me in 10 minutes to check the oven"`)
- Calculator (`"calculate 15 * 340"`)
- Weather via [wttr.in](https://wttr.in) — no API key required
- Daily briefing — date, time, weather, note count, motivational quote
- Clipboard read and copy
- Dictation mode — speak and type into any active app

### 💻 System Controls (macOS)
- Volume control — set, mute, unmute
- Brightness control — increase or decrease
- Battery status
- Screenshot — saved to `screenshots/`
- Open apps and websites
- Web search (Google)

### 🔐 Safety
- Confirmation prompts for destructive or impactful actions
- Blocked actions policy for unknown commands
- Configurable confirmation toggle via `.env`

### 🛠️ Developer
- 24 unit tests with `pytest`
- Logging to `jarvis.log`
- Modular architecture — easy to add new commands

---

## 🖥️ Requirements

- macOS (Apple Silicon or Intel)
- Python 3.11+
- [Ollama](https://ollama.com) installed and running
- [Homebrew](https://brew.sh) (for PortAudio)

---

## 🚀 Setup

### 1. Install system dependencies

```bash
brew install portaudio
```

### 2. Clone the repository

```bash
git clone https://github.com/Calvin2506/Jarvis-AI.git
cd Jarvis-AI
```

### 3. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 5. Install and start Ollama

```bash
# Install Ollama from https://ollama.com
ollama pull qwen3:8b
ollama serve
```

### 6. Configure environment

```bash
cp .env.example .env
```

Edit `.env` as needed:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL_NAME=qwen3:8b
OLLAMA_TIMEOUT_SECONDS=60
CONFIRM_ACTIONS=true
MICROPHONE_DEVICE_INDEX=1
```

> To find your microphone index, run:
> ```bash
> python3 -c "import speech_recognition as sr; print(list(enumerate(sr.Microphone.list_microphone_names())))"
> ```

### 7. Grant microphone permission

Go to **System Settings → Privacy & Security → Microphone** and enable access for **Terminal**.

### 8. Run Jarvis

```bash
python3 main.py
```

---

## 🗣️ Available Commands

### General
| Command | Description |
|---|---|
| `hello` / `hi` / `hey` | Greeting |
| `what time is it` | Current time |
| `what is the date` | Current date |
| `repeat <text>` | Repeat back any text |
| `show history` | Show conversation history |
| `exit` | Shut down Jarvis |

### Notes
| Command | Description |
|---|---|
| `note <text>` | Save a new note |
| `list notes` | List all saved notes |
| `read note <number or name>` | Read a specific note |
| `read aloud <number or name>` | Read a note aloud |
| `delete note <number or name>` | Delete a note (requires confirmation) |
| `summarize note <number or name>` | Summarise a note via Ollama |

### Productivity
| Command | Description |
|---|---|
| `remind me in <duration> to <task>` | Set a reminder |
| `calculate <expression>` | Evaluate a math expression |
| `weather` / `weather in <city>` | Get current weather |
| `good morning` / `daily briefing` | Morning summary |
| `read clipboard` | Read clipboard contents |
| `copy <text> to clipboard` | Copy text to clipboard |
| `start dictation` | Dictate text into active app |
| `stop dictation` | Stop dictation mode |

### System Controls
| Command | Description |
|---|---|
| `set volume <0-100>` | Set system volume |
| `mute` / `unmute` | Mute or unmute audio |
| `increase brightness` / `decrease brightness` | Adjust screen brightness |
| `battery status` | Show battery level |
| `take a screenshot` | Save a screenshot |
| `open app <name>` | Open a macOS app |
| `open website <url>` | Open a website |
| `search <topic>` | Search Google |

### LLM & Intelligence
| Command | Description |
|---|---|
| `persona <name>` | Switch persona (`default`, `formal`, `casual`, `concise`) |
| `play` / `pause` / `next song` / `previous song` | Music control (Spotify / Apple Music) |
| `run code <snippet>` | Execute a Python snippet (requires confirmation) |
| Any other input | Sent to Ollama for a conversational response |

---

## 📁 Project Structure

```
jarvis-ai/
├── main.py                  # Entry point — input loop, mode switching
├── assistant/
│   ├── brain.py             # Command router
│   ├── commands.py          # All command implementations
│   ├── config.py            # Environment config and persona prompts
│   ├── errors.py            # Error handling and logging
│   ├── history.py           # Conversation history (history.json)
│   ├── llm.py               # Ollama LLM integration
│   ├── memory.py            # Persistent memory (memory.json)
│   ├── safety.py            # Action policies (safe / confirm / blocked)
│   ├── validation.py        # Input validators
│   └── voice.py             # Microphone input and TTS output
├── tests/
│   ├── test_brain.py        # Routing tests
│   ├── test_commands.py     # Command unit tests
│   └── test_validation.py   # Validator tests
├── notes/                   # Saved note files
├── screenshots/             # Saved screenshots
├── .env.example             # Environment variable template
├── requirements.txt         # Python dependencies
└── jarvis.log               # Runtime log file
```

---

## 🧪 Running Tests

```bash
python3 -m pytest tests/ -v
```

---

## 🔒 Privacy

- All LLM inference runs **locally** via Ollama — nothing is sent to the cloud
- Speech-to-text uses **OpenAI Whisper** running on-device
- Notes and memory are stored as plain local files

---

## 📄 License

MIT License — free to use, modify, and distribute.