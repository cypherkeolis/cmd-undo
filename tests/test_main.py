import json
import os
import tempfile
import pytest
import subprocess
from datetime import datetime
import main


def test_load_history_no_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "nonexistent.jsonl")
        assert main.load_history(path) == []


def test_load_history_parses_jsonl():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "history.jsonl")
        entries = [
            {"timestamp": "2020-01-01T00:00:00", "command": "ls", "exit_code": 0},
            {"timestamp": "2020-01-01T00:00:01", "command": "pwd", "exit_code": 0},
        ]
        with open(path, "w") as f:
            for e in entries:
                f.write(json.dumps(e) + "\n")
        loaded = main.load_history(path)
        assert len(loaded) == 2
        assert loaded[0]["command"] == "ls"
        assert loaded[1]["command"] == "pwd"


def test_load_history_ignores_invalid_lines():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "history.jsonl")
        with open(path, "w") as f:
            f.write(json.dumps({"timestamp": "2020-01-01T00:00:00", "command": "ls", "exit_code": 0}) + "\n")
            f.write("invalid json line\n")
            f.write(json.dumps({"timestamp": "2020-01-01T00:00:01", "command": "pwd", "exit_code": 0}) + "\n")
        loaded = main.load_history(path)
        assert len(loaded) == 2


def test_load_history_limits_to_max_entries():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "history.jsonl")
        with open(path, "w") as f:
            for i in range(60):
                f.write(json.dumps({"timestamp": f"2020-01-01T00:00:{i:02d}", "command": f"cmd{i}", "exit_code": 0}) + "\n")
        loaded = main.load_history(path)
        assert len(loaded) == main.MAX_ENTRIES
        assert loaded[0]["command"] == "cmd10"
        assert loaded[-1]["command"] == "cmd59"


def test_save_history_writes_jsonl():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "history.jsonl")
        entries = [
            {"timestamp": "2020-01-01T00:00:00", "command": "ls", "exit_code": 0},
            {"timestamp": "2020-01-01T00:00:01", "command": "pwd", "exit_code": 0},
        ]
        main.save_history(entries, path)
        with open(path, "r") as f:
            lines = f.readlines()
        assert len(lines) == 2
        assert json.loads(lines[0])["command"] == "ls"
        assert json.loads(lines[1])["command"] == "pwd"


def test_save_history_limits_to_max_entries():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "history.jsonl")
        entries = [{"timestamp": f"2020-01-01T00:00:{i:02d}", "command": f"cmd{i}", "exit_code": 0} for i in range(60)]
        main.save_history(entries, path)
        with open(path, "r") as f:
            lines = f.readlines()
        assert len(lines) == main.MAX_ENTRIES


def test_log_command_appends_entry():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "history.jsonl")
        entry = main.log_command("ls -la", 0, path)
        assert entry["command"] == "ls -la"
        assert entry["exit_code"] == 0
        loaded = main.load_history(path)
        assert len(loaded) == 1
        assert loaded[0]["command"] == "ls -la"


def test_list_recent_returns_last_n():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "history.jsonl")
        for i in range(10):
            main.log_command(f"cmd{i}", 0, path)
        recent = main.list_recent(3, path)
        assert len(recent) == 3
        assert recent[0]["command"] == "cmd7"
        assert recent[-1]["command"] == "cmd9"


def test_search_history_finds_keyword():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "history.jsonl")
        main.log_command("ls -la", 0, path)
        main.log_command("cd /tmp", 0, path)
        main.log_command("ls /var", 0, path)
        results = main.search_history("ls", path)
        assert len(results) == 2
        assert results[0]["command"] == "ls -la"
        assert results[1]["command"] == "ls /var"


def test_suggest_undo_rm_in_git_repo():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        subprocess.run(["git", "init"], capture_output=True)
        result = main.suggest_undo("rm file.txt")
        assert result == "git checkout -- file.txt"


def test_suggest_undo_rm_not_in_git_repo():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.chdir(tmpdir)
        result = main.suggest_undo("rm file.txt")
        assert "Warning" in result


def test_suggest_undo_mv():
    result = main.suggest_undo("mv src.txt dst.txt")
    assert result == "mv dst.txt src.txt"


def test_suggest_undo_cp():
    result = main.suggest_undo("cp src.txt dst.txt")
    assert result == "rm dst.txt"


def test_suggest_undo_unknown():
    result = main.suggest_undo("echo hello")
    assert "No inverse operation known" in result


def test_suggest_undo_empty():
    result = main.suggest_undo("")
    assert "Cannot determine inverse" in result
