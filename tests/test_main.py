import os
import json
import sys
import pytest
from unittest.mock import patch
from datetime import datetime

# Import functions from main
from main import (
    load_history,
    save_history,
    add_command,
    get_last_n,
    suggest_inverse,
    list_commands,
    undo_last,
    main,
    HISTORY_FILE,
    MAX_HISTORY,
    INVERSE_MAP,
)


@pytest.fixture(autouse=True)
def clean_history_file():
    """Ensure the history file is removed before and after each test."""
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)
    yield
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)


class TestLoadHistory:
    def test_returns_empty_list_when_file_does_not_exist(self):
        assert load_history() == []

    def test_returns_parsed_json_when_file_exists(self):
        data = [{"command": "ls", "timestamp": "2023-01-01T00:00:00"}]
        with open(HISTORY_FILE, 'w') as f:
            json.dump(data, f)
        assert load_history() == data


class TestSaveHistory:
    def test_saves_history_to_file(self):
        history = [{"command": "ls", "timestamp": "2023-01-01T00:00:00"}]
        save_history(history)
        assert os.path.exists(HISTORY_FILE)
        with open(HISTORY_FILE, 'r') as f:
            loaded = json.load(f)
        assert loaded == history


class TestAddCommand:
    def test_adds_command_and_saves(self):
        result = add_command("ls -la")
        assert len(result) == 1
        assert result[0]['command'] == "ls -la"
        assert 'timestamp' in result[0]
        # Verify file was saved
        with open(HISTORY_FILE, 'r') as f:
            data = json.load(f)
        assert data == result

    def test_truncates_to_max_history(self):
        # Add MAX_HISTORY + 1 commands
        for i in range(MAX_HISTORY + 1):
            add_command(f"cmd_{i}")
        history = load_history()
        assert len(history) == MAX_HISTORY
        # The oldest command (cmd_0) should be removed
        assert history[0]['command'] == "cmd_1"
        assert history[-1]['command'] == f"cmd_{MAX_HISTORY}"

    def test_returns_updated_history(self):
        add_command("first")
        result = add_command("second")
        assert len(result) == 2
        assert result[0]['command'] == "first"
        assert result[1]['command'] == "second"


class TestGetLastN:
    def test_returns_empty_list_when_no_history(self):
        assert get_last_n() == []

    def test_returns_last_n_commands(self):
        for i in range(5):
            add_command(f"cmd_{i}")
        result = get_last_n(3)
        assert len(result) == 3
        assert result[0]['command'] == "cmd_2"
        assert result[1]['command'] == "cmd_3"
        assert result[2]['command'] == "cmd_4"

    def test_returns_all_when_n_greater_than_history_length(self):
        for i in range(3):
            add_command(f"cmd_{i}")
        result = get_last_n(10)
        assert len(result) == 3
        assert result[0]['command'] == "cmd_0"
        assert result[-1]['command'] == "cmd_2"


class TestSuggestInverse:
    def test_mkdir(self):
        assert suggest_inverse("mkdir mydir") == "rmdir"

    def test_rm(self):
        assert suggest_inverse("rm file.txt") == "touch"

    def test_touch(self):
        assert suggest_inverse("touch file.txt") == "rm"

    def test_git_commit(self):
        assert suggest_inverse("git commit -m 'msg'") == "git reset --soft HEAD~1"

    def test_git_push(self):
        assert suggest_inverse("git push origin main") == "git push --delete"

    def test_git_checkout(self):
        assert suggest_inverse("git checkout main") == "git checkout"

    def test_cd(self):
        assert suggest_inverse("cd /home") == "cd"

    def test_no_match_returns_none(self):
        assert suggest_inverse("echo hello") is None

    def test_case_insensitive(self):
        assert suggest_inverse("MKDIR mydir") == "rmdir"

    def test_strips_whitespace(self):
        assert suggest_inverse("  mkdir mydir  ") == "rmdir"


class TestListCommands:
    def test_no_history(self):
        assert list_commands() == "No commands in history."

    def test_lists_commands_with_timestamps(self):
        add_command("ls")
        add_command("pwd")
        result = list_commands()
        lines = result.split('\n')
        assert len(lines) == 2
        assert lines[0].startswith("1. [")
        assert lines[0].endswith("ls")
        assert lines[1].startswith("2. [")
        assert lines[1].endswith("pwd")

    def test_respects_n_parameter(self):
        for i in range(5):
            add_command(f"cmd_{i}")
        result = list_commands(3)
        lines = result.split('\n')
        assert len(lines) == 3
        assert "cmd_2" in lines[0]
        assert "cmd_3" in lines[1]
        assert "cmd_4" in lines[2]


class TestUndoLast:
    def test_no_history(self):
        assert undo_last() == "No commands to undo."

    def test_with_inverse_suggestion(self):
        add_command("mkdir mydir")
        result = undo_last()
        assert "Last command: mkdir mydir" in result
        assert "Suggested inverse: rmdir" in result

    def test_without_inverse_suggestion(self):
        add_command("echo hello")
        result = undo_last()
        assert "Last command: echo hello" in result
        assert "No inverse suggestion available." in result


class TestMain:
    def test_no_args_shows_usage_and_history(self, capsys):
        with patch.object(sys, 'argv', ['main.py']):
            main()
        captured = capsys.readouterr()
        assert "Usage:" in captured.out
        assert "No commands in history." in captured.out

    def test_list_command(self, capsys):
        add_command("ls")
        with patch.object(sys, 'argv', ['main.py', 'list']):
            main()
        captured = capsys.readouterr()
        assert "ls" in captured.out

    def test_undo_command(self, capsys):
        add_command("mkdir test")
        with patch.object(sys, 'argv', ['main.py', 'undo']):
            main()
        captured = capsys.readouterr()
        assert "Suggested inverse: rmdir" in captured.out

    def test_log_command(self, capsys):
        with patch.object(sys, 'argv', ['main.py', 'log', 'ls', '-la']):
            main()
        captured = capsys.readouterr()
        assert "Logged: ls -la" in captured.out
        history = load_history()
        assert len(history) == 1
        assert history[0]['command'] == "ls -la"

    def test_log_command_without_args(self, capsys):
        with patch.object(sys, 'argv', ['main.py', 'log']):
            main()
        captured = capsys.readouterr()
        assert "Usage: python3 main.py log <command>" in captured.out

    def test_unknown_command(self, capsys):
        with patch.object(sys, 'argv', ['main.py', 'unknown']):
            main()
        captured = capsys.readouterr()
        assert "Unknown command" in captured.out
