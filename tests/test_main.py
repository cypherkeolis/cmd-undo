import pytest
import os
import json
import tempfile
from unittest.mock import patch
from datetime import datetime

from main import (
    load_history,
    save_history,
    log_command,
    get_reverse_operation,
    undo_last_command,
    search_commands,
    HISTORY_FILE,
)


class TestLoadHistory:
    def test_returns_empty_list_when_file_does_not_exist(self, tmp_path):
        path = str(tmp_path / "nonexistent.json")
        assert load_history(path) == []

    def test_returns_list_when_file_exists(self, tmp_path):
        data = [{"command": "ls", "timestamp": "2024-01-01T00:00:00"}]
        path = str(tmp_path / "hist.json")
        with open(path, "w") as f:
            json.dump(data, f)
        result = load_history(path)
        assert result == data


class TestSaveHistory:
    def test_saves_history_to_file(self, tmp_path):
        path = str(tmp_path / "hist.json")
        data = [{"command": "ls", "timestamp": "2024-01-01T00:00:00"}]
        save_history(data, path)
        with open(path, "r") as f:
            loaded = json.load(f)
        assert loaded == data


class TestLogCommand:
    def test_appends_command_to_history(self, tmp_path):
        path = str(tmp_path / "hist.json")
        history = log_command("ls -la", path=path)
        assert len(history) == 1
        assert history[0]["command"] == "ls -la"
        assert "timestamp" in history[0]

    def test_appends_to_existing_history(self, tmp_path):
        path = str(tmp_path / "hist.json")
        initial = [{"command": "pwd", "timestamp": "2024-01-01T00:00:00"}]
        history = log_command("ls", history=initial, path=path)
        assert len(history) == 2
        assert history[0]["command"] == "pwd"
        assert history[1]["command"] == "ls"


class TestGetReverseOperation:
    def test_rm_returns_warning(self):
        result = get_reverse_operation("rm file.txt")
        assert "WARNING" in result
        assert "rm" in result

    def test_mv_returns_reversed(self):
        result = get_reverse_operation("mv a.txt b.txt")
        assert result == "mv b.txt a.txt"

    def test_mv_with_multiple_args(self):
        result = get_reverse_operation("mv src.txt dst.txt")
        assert result == "mv dst.txt src.txt"

    def test_cp_returns_warning(self):
        result = get_reverse_operation("cp source.txt backup.txt")
        assert "WARNING" in result
        assert "cp" in result

    def test_mkdir_returns_rmdir(self):
        result = get_reverse_operation("mkdir new_dir")
        assert result == "rmdir new_dir"

    def test_touch_returns_rm(self):
        result = get_reverse_operation("touch file.txt")
        assert result == "rm file.txt"

    def test_unknown_command_returns_warning(self):
        result = get_reverse_operation("echo hello")
        assert "WARNING" in result
        assert "echo" in result

    def test_empty_command(self):
        result = get_reverse_operation("")
        assert "Cannot determine" in result


class TestUndoLastCommand:
    def test_returns_warning_for_rm(self, tmp_path):
        path = str(tmp_path / "hist.json")
        history = [{"command": "rm old.txt", "timestamp": "2024-01-01T00:00:00"}]
        result = undo_last_command(history=history, path=path)
        assert "WARNING" in result

    def test_returns_reversed_mv(self, tmp_path):
        path = str(tmp_path / "hist.json")
        history = [{"command": "mv a.txt b.txt", "timestamp": "2024-01-01T00:00:00"}]
        result = undo_last_command(history=history, path=path)
        assert result == "mv b.txt a.txt"

    def test_returns_message_when_history_empty(self, tmp_path):
        path = str(tmp_path / "hist.json")
        result = undo_last_command(history=[], path=path)
        assert "No commands" in result


class TestSearchCommands:
    def test_finds_matching_commands(self, tmp_path):
        path = str(tmp_path / "hist.json")
        history = [
            {"command": "mv a.txt b.txt", "timestamp": "2024-01-01T00:00:00"},
            {"command": "ls -la", "timestamp": "2024-01-01T00:01:00"},
            {"command": "mv c.txt d.txt", "timestamp": "2024-01-01T00:02:00"},
        ]
        results = search_commands("mv", history=history, path=path)
        assert len(results) == 2
        assert results[0]["command"] == "mv a.txt b.txt"
        assert results[1]["command"] == "mv c.txt d.txt"

    def test_case_insensitive_search(self, tmp_path):
        path = str(tmp_path / "hist.json")
        history = [{"command": "MV a.txt b.txt", "timestamp": "2024-01-01T00:00:00"}]
        results = search_commands("mv", history=history, path=path)
        assert len(results) == 1

    def test_no_matches_returns_empty_list(self, tmp_path):
        path = str(tmp_path / "hist.json")
        history = [{"command": "ls", "timestamp": "2024-01-01T00:00:00"}]
        results = search_commands("rm", history=history, path=path)
        assert results == []

    def test_empty_history_returns_empty_list(self, tmp_path):
        path = str(tmp_path / "hist.json")
        results = search_commands("mv", history=[], path=path)
        assert results == []
