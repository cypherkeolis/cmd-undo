import json
import os
import sys
import re
from datetime import datetime

HISTORY_FILE = 'command_history.json'
MAX_HISTORY = 10

INVERSE_MAP = {
    'mkdir': 'rmdir',
    'rm': 'touch',
    'touch': 'rm',
    'git commit': 'git reset --soft HEAD~1',
    'git push': 'git push --delete',
    'git checkout': 'git checkout',
    'cd': 'cd',
}


def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []


def save_history(history):
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)


def add_command(cmd):
    history = load_history()
    entry = {'command': cmd, 'timestamp': datetime.now().isoformat()}
    history.append(entry)
    if len(history) > MAX_HISTORY:
        history = history[-MAX_HISTORY:]
    save_history(history)
    return history


def get_last_n(n=10):
    history = load_history()
    return history[-n:]


def suggest_inverse(cmd):
    cmd_lower = cmd.lower().strip()
    for pattern, inverse in INVERSE_MAP.items():
        if cmd_lower.startswith(pattern):
            return inverse
    return None


def list_commands(n=10):
    history = get_last_n(n)
    if not history:
        return 'No commands in history.'
    lines = []
    for i, entry in enumerate(history, 1):
        lines.append(f"{i}. [{entry['timestamp']}] {entry['command']}")
    return '\n'.join(lines)


def undo_last():
    history = get_last_n(1)
    if not history:
        return 'No commands to undo.'
    last_cmd = history[-1]['command']
    inverse = suggest_inverse(last_cmd)
    if inverse:
        return f"Last command: {last_cmd}\nSuggested inverse: {inverse}"
    return f"Last command: {last_cmd}\nNo inverse suggestion available."


def main():
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == 'list':
            print(list_commands())
        elif cmd == 'undo':
            print(undo_last())
        elif cmd == 'log':
            if len(sys.argv) > 2:
                logged_cmd = ' '.join(sys.argv[2:])
                add_command(logged_cmd)
                print(f"Logged: {logged_cmd}")
            else:
                print("Usage: python3 main.py log <command>")
        else:
            print("Unknown command. Use: list, undo, log")
    else:
        print("Usage: python3 main.py [list|undo|log <command>]")
        print("Default: showing recent history")
        print(list_commands())


if __name__ == '__main__':
    main()
