import json
import os
import sys
import re
from datetime import datetime

HISTORY_FILE = "command_history.json"

def load_history(path=HISTORY_FILE):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return []

def save_history(history, path=HISTORY_FILE):
    with open(path, "w") as f:
        json.dump(history, f, indent=2)

def log_command(command, history=None, path=HISTORY_FILE):
    if history is None:
        history = load_history(path)
    history.append({"command": command, "timestamp": datetime.now().isoformat()})
    save_history(history, path)
    return history

def get_reverse_operation(command):
    parts = command.split()
    if not parts:
        return "Cannot determine reverse operation"
    cmd = parts[0]
    if cmd == "rm":
        return f"WARNING: Cannot undo 'rm'. Files may be permanently deleted."
    elif cmd == "mv" and len(parts) >= 3:
        return f"mv {parts[-1]} {parts[-2]}"
    elif cmd == "cp" and len(parts) >= 3:
        return f"WARNING: Cannot safely undo 'cp'. Consider removing '{parts[-1]}' if no longer needed."
    elif cmd == "mkdir" and len(parts) >= 2:
        return f"rmdir {parts[-1]}"
    elif cmd == "touch" and len(parts) >= 2:
        return f"rm {parts[-1]}"
    else:
        return f"WARNING: No safe reverse operation defined for '{cmd}'"

def undo_last_command(history=None, path=HISTORY_FILE):
    if history is None:
        history = load_history(path)
    if not history:
        return "No commands in history to undo"
    last_cmd = history[-1]["command"]
    return get_reverse_operation(last_cmd)

def search_commands(keyword, history=None, path=HISTORY_FILE):
    if history is None:
        history = load_history(path)
    results = []
    for entry in history:
        if keyword.lower() in entry["command"].lower():
            results.append(entry)
    return results

def main():
    history = load_history()
    if not history:
        history = [
            {"command": "rm old_file.txt", "timestamp": "2024-01-01T10:00:00"},
            {"command": "mv a.txt b.txt", "timestamp": "2024-01-01T10:05:00"},
            {"command": "mkdir new_dir", "timestamp": "2024-01-01T10:10:00"},
            {"command": "cp source.txt backup.txt", "timestamp": "2024-01-01T10:15:00"}
        ]
        save_history(history)
    print("Command History Manager")
    print("=" * 40)
    print(f"Total commands logged: {len(history)}")
    print("\nLast 5 commands:")
    for entry in history[-5:]:
        print(f"  [{entry['timestamp']}] {entry['command']}")
    print("\nUndo last command:")
    print(f"  {undo_last_command(history)}")
    print("\nSearch for 'mv':")
    results = search_commands("mv", history)
    if results:
        for entry in results:
            print(f"  [{entry['timestamp']}] {entry['command']}")
    else:
        print("  No matching commands found")

if __name__ == '__main__':
    main()
