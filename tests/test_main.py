import json
import os
import sys
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import main


@pytest.fixture(autouse=True)
def setup_teardown(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "LOG_FILE", str(tmp_path / "command_log.json"))
    yield


def test_load_log_empty():
    assert main.load_log() == []


def test_save_and_load_log():
    log_data = [{"command": "ls"}, {"command": "pwd"}]
    main.save_log(log_data)
    loaded = main.load_log()
    assert loaded == log_data


def test_log_command():
    cmd = "ls -l"
    result = main.log_command(cmd)
    assert result == cmd
    log = main.load_log()
    assert log == [{"command": cmd}]


def test_log_command_multiple():
    main.log_command("ls")
    main.log_command("pwd")
    log = main.load_log()
    assert log == [{"command": "ls"}, {"command": "pwd"}]


def test_get_inverse_rm():
    assert main.get_inverse("rm file.txt") == "git checkout -- file.txt"
    assert main.get_inverse("rm -rf dir") == "git checkout -- -rf dir"


def test_get_inverse_mkdir():
    assert main.get_inverse("mkdir new_dir") == "rmdir new_dir"


def test_get_inverse_cp():
    assert main.get_inverse("cp src.txt dst.txt") == "mv dst.txt src.txt"
    assert main.get_inverse("cp src.txt dst.txt extra") == "mv dst.txt src.txt"


def test_get_inverse_mv():
    assert main.get_inverse("mv src.txt dst.txt") == "mv dst.txt src.txt"


def test_get_inverse_touch():
    assert main.get_inverse("touch file.txt") == "rm file.txt"


def test_get_inverse_unknown():
    assert main.get_inverse("echo hello") is None
    assert main.get_inverse("") is None


def test_undo_last_empty_log():
    assert main.undo_last() is None


def test_undo_last_no_inverse():
    main.log_command("echo hello")
    assert main.undo_last() is None
    assert main.load_log() == [{"command": "echo hello"}]


def test_undo_last_with_inverse():
    main.log_command("rm file.txt")
    inverse = main.undo_last()
    assert inverse == "git checkout -- file.txt"
    assert main.load_log() == []


def test_undo_last_multiple_commands():
    main.log_command("mkdir dir1")
    main.log_command("touch dir1/file.txt")
    main.log_command("rm dir1/file.txt")
    
    inverse = main.undo_last()
    assert inverse == "git checkout -- dir1/file.txt"
    
    log = main.load_log()
    assert log == [{"command": "mkdir dir1"}, {"command": "touch dir1/file.txt"}]
    
    inverse2 = main.undo_last()
    assert inverse2 == "rm dir1/file.txt"
    
    log = main.load_log()
    assert log == [{"command": "mkdir dir1"}]
