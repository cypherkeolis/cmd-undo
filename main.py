import json
import os
import sys
import time
from datetime import datetime

HISTORY_FILE = "command_history.json"
MAX_ENTRIES = 5

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except (json.JSONDecodeError, IOError):
        return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def add_command(command, exit_code=0):
    history = load_history()
    entry = {
        "command": command,
        "exit_code": exit_code,
        "timestamp": datetime.now().isoformat()
    }
    history.append(entry)
    if len(history) > MAX_ENTRIES:
        history = history[-MAX_ENTRIES:]
    save_history(history)
    return entry

def get_recent_history(n=MAX_ENTRIES):
    history = load_history()
    return history[-n:]

def get_command_by_index(index):
    history = load_history()
    if 0 <= index < len(history):
        return history[index]
    return None

def list_commands():
    history = get_recent_history()
    if not history:
        print("No commands recorded.")
        return
    for i, entry in enumerate(history):
        print(f"[{i}] {entry['timestamp']} | exit={entry['exit_code']} | {entry['command']}")

def replay_command(index):
    entry = get_command_by_index(index)
    if entry is None:
        print(f"Invalid index: {index}")
        return
    print(entry["command"])

def main():
    args = sys.argv[1:]
    if not args:
        list_commands()
        return
    cmd = args[0]
    if cmd == "list":
        list_commands()
    elif cmd == "replay":
        if len(args) < 2:
            print("Usage: python3 main.py replay <index>")
            return
        try:
            index = int(args[1])
        except ValueError:
            print("Index must be an integer.")
            return
        replay_command(index)
    elif cmd == "add":
        if len(args) < 2:
            print("Usage: python3 main.py add <command> [exit_code]")
            return
        command = args[1]
        exit_code = 0
        if len(args) >= 3:
            try:
                exit_code = int(args[2])
            except ValueError:
                exit_code = 0
        add_command(command, exit_code)
        print("Command recorded.")
    else:
        print("Unknown command. Use: list, replay, add")

if __name__ == "__main__":
    main()
