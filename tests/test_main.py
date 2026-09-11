import json
import os
import sys
import pytest
from unittest.mock import patch
from datetime import datetime

import main

HISTORY_FILE = main.HISTORY_FILE
MAX_ENTRIES = main.MAX_ENTRIES

@pytest.fixture(autouse=True)
def clean_history_file():
    """Ensure a clean history file before and after each test."""
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
    yield
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)

def test_load_history_no_file():
    assert main.load_history() == []

def test_load_history_empty_list():
    with open(HISTORY_FILE, "w") as f:
        json.dump([], f)
    assert main.load_history() == []

def test_load_history_valid_data():
    data = [
        {"command": "ls", "exit_code": 0, "timestamp": "2023-01-01T00:00:00"},
        {"command": "pwd", "exit_code": 0, "timestamp": "2023-01-01T00:01:00"},
    ]
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f)
    result = main.load_history()
    assert result == data

def test_load_history_invalid_json():
    with open(HISTORY_FILE, "w") as f:
        f.write("{invalid json")
    assert main.load_history() == []

def test_load_history_not_a_list():
    with open(HISTORY_FILE, "w") as f:
        json.dump({"key": "value"}, f)
    assert main.load_history() == []

def test_save_history():
    data = [
        {"command": "ls", "exit_code": 0, "timestamp": "2023-01-01T00:00:00"},
    ]
    main.save_history(data)
    with open(HISTORY_FILE, "r") as f:
        loaded = json.load(f)
    assert loaded == data

def test_add_command_creates_entry():
    entry = main.add_command("ls -la", 0)
    assert entry["command"] == "ls -la"
    assert entry["exit_code"] == 0
    assert "timestamp" in entry
    history = main.load_history()
    assert len(history) == 1
    assert history[0] == entry

def test_add_command_with_nonzero_exit_code():
    entry = main.add_command("false", 1)
    assert entry["exit_code"] == 1
    history = main.load_history()
    assert history[0]["exit_code"] == 1

def test_add_command_max_entries_limit():
    for i in range(MAX_ENTRIES + 2):
        main.add_command(f"cmd_{i}", 0)
    history = main.load_history()
    assert len(history) == MAX_ENTRIES
    # The oldest entries should have been dropped
    assert history[0]["command"] == f"cmd_2"
    assert history[-1]["command"] == f"cmd_{MAX_ENTRIES + 1}"

def test_get_recent_history_all():
    for i in range(MAX_ENTRIES):
        main.add_command(f"cmd_{i}", 0)
    recent = main.get_recent_history()
    assert len(recent) == MAX_ENTRIES
    for i, entry in enumerate(recent):
        assert entry["command"] == f"cmd_{i}"

def test_get_recent_history_n():
    for i in range(MAX_ENTRIES):
        main.add_command(f"cmd_{i}", 0)
    recent = main.get_recent_history(3)
    assert len(recent) == 3
    assert recent[0]["command"] == f"cmd_{MAX_ENTRIES - 3}"
    assert recent[-1]["command"] == f"cmd_{MAX_ENTRIES - 1}"

def test_get_recent_history_empty():
    assert main.get_recent_history() == []

def test_get_command_by_index_valid():
    main.add_command("ls", 0)
    main.add_command("pwd", 0)
    entry = main.get_command_by_index(0)
    assert entry["command"] == "ls"
    entry = main.get_command_by_index(1)
    assert entry["command"] == "pwd"

def test_get_command_by_index_out_of_range():
    main.add_command("ls", 0)
    assert main.get_command_by_index(5) is None
    assert main.get_command_by_index(-1) is None

def test_list_commands_empty(capsys):
    main.list_commands()
    captured = capsys.readouterr()
    assert "No commands recorded." in captured.out

def test_list_commands_with_entries(capsys):
    main.add_command("ls", 0)
    main.add_command("pwd", 1)
    main.list_commands()
    captured = capsys.readouterr()
    assert "[0]" in captured.out
    assert "ls" in captured.out
    assert "exit=0" in captured.out
    assert "[1]" in captured.out
    assert "pwd" in captured.out
    assert "exit=1" in captured.out

def test_replay_command_valid(capsys):
    main.add_command("ls -la", 0)
    main.add_command("pwd", 0)
    main.replay_command(0)
    captured = capsys.readouterr()
    assert captured.out.strip() == "ls -la"
    main.replay_command(1)
    captured = capsys.readouterr()
    assert captured.out.strip() == "pwd"

def test_replay_command_invalid_index(capsys):
    main.add_command("ls", 0)
    main.replay_command(99)
    captured = capsys.readouterr()
    assert "Invalid index: 99" in captured.out

def test_main_no_args_lists_commands(capsys):
    main.add_command("ls", 0)
    with patch.object(sys, "argv", ["main.py"]):
        main.main()
    captured = capsys.readouterr()
    assert "ls" in captured.out

def test_main_list_command(capsys):
    main.add_command("ls", 0)
    with patch.object(sys, "argv", ["main.py", "list"]):
        main.main()
    captured = capsys.readouterr()
    assert "ls" in captured.out

def test_main_replay_command(capsys):
    main.add_command("ls -la", 0)
    with patch.object(sys, "argv", ["main.py", "replay", "0"]):
        main.main()
    captured = capsys.readouterr()
    assert "ls -la" in captured.out

def test_main_replay_no_index(capsys):
    with patch.object(sys, "argv", ["main.py", "replay"]):
        main.main()
    captured = capsys.readouterr()
    assert "Usage:" in captured.out

def test_main_replay_non_integer_index(capsys):
    with patch.object(sys, "argv", ["main.py", "replay", "abc"]):
        main.main()
    captured = capsys.readouterr()
    assert "Index must be an integer." in captured.out

def test_main_add_command(capsys):
    with patch.object(sys, "argv", ["main.py", "add", "ls", "0"]):
        main.main()
    captured = capsys.readouterr()
    assert "Command recorded." in captured.out
    history = main.load_history()
    assert len(history) == 1
    assert history[0]["command"] == "ls"
    assert history[0]["exit_code"] == 0

def test_main_add_command_no_exit_code(capsys):
    with patch.object(sys, "argv", ["main.py", "add", "pwd"]):
        main.main()
    captured = capsys.readouterr()
    assert "Command recorded." in captured.out
    history = main.load_history()
    assert history[0]["command"] == "pwd"
    assert history[0]["exit_code"] == 0

def test_main_add_command_non_integer_exit_code(capsys):
    with patch.object(sys, "argv", ["main.py", "add", "ls", "notanint"]):
        main.main()
    captured = capsys.readouterr()
    assert "Command recorded." in captured.out
    history = main.load_history()
    assert history[0]["exit_code"] == 0

def test_main_add_no_command(capsys):
    with patch.object(sys, "argv", ["main.py", "add"]):
        main.main()
    captured = capsys.readouterr()
    assert "Usage:" in captured.out

def test_main_unknown_command(capsys):
    with patch.object(sys, "argv", ["main.py", "unknown"]):
        main.main()
    captured = capsys.readouterr()
    assert "Unknown command" in captured.out

def test_timestamp_is_iso_format():
    entry = main.add_command("ls", 0)
    # Should be parseable as ISO format
    datetime.fromisoformat(entry["timestamp"])
