from assistant.brain import route_command


def test_hello():
    assert route_command("hello")["action_name"] == "say_hello"


def test_hi():
    assert route_command("hi")["action_name"] == "say_hello"


def test_hey():
    assert route_command("hey")["action_name"] == "say_hello"


def test_time():
    assert route_command("what time is it")["action_name"] == "tell_time"


def test_date():
    assert route_command("what is the date")["action_name"] == "tell_date"


def test_search():
    assert route_command("search python tutorials")["action_name"] == "search_topic"


def test_list_notes():
    assert route_command("list notes")["action_name"] == "list_notes"


def test_delete_note():
    assert route_command("delete note 1")["action_name"] == "delete_note"


def test_weather():
    assert route_command("weather in Chennai")["action_name"] == "get_weather"


def test_calculate():
    assert route_command("calculate 10 * 5")["action_name"] == "calculate"


def test_battery():
    assert route_command("battery status")["action_name"] == "get_battery"


def test_mute():
    assert route_command("mute")["action_name"] == "set_volume"


def test_unknown_falls_back_to_llm():
    assert route_command("xkcd random gibberish 123")["action_name"] == "ask_llm"
