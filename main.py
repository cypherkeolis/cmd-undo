import json
import os
import subprocess
import argparse
import datetime
import shlex

HISTORY_FILE = ".cmd_history.jsonl"
MAX_ENTRIES = 50

def load_history(path=HISTORY_FILE):
    if not os.path.exists(path):
        return []
    entries = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return entries[-MAX_ENTRIES:]

def save_history(entries, path=HISTORY_FILE):
    with open(path, "w") as f:
        for e in entries[-MAX_ENTRIES:]:
            f.write(json.dumps(e) + "\n")

def log_command(cmd, exit_code, path=HISTORY_FILE):
    entries = load_history(path)
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "command": cmd,
        "exit_code": exit_code
    }
    entries.append(entry)
    save_history(entries, path)
    return entry

def list_recent(n=10, path=HISTORY_FILE):
    entries = load_history(path)
    return entries[-n:]

def search_history(keyword, path=HISTORY_FILE):
    entries = load_history(path)
    return [e for e in entries if keyword.lower() in e["command"].lower()]

def suggest_undo(cmd, path=HISTORY_FILE):
    parts = shlex.split(cmd)
    if not parts:
        return "Cannot determine inverse for empty command."
    cmd_name = parts[0]
    if cmd_name == "rm" and len(parts) > 1:
        target = parts[-1]
        try:
            result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                return f"git checkout -- {target}"
        except Exception:
            pass
        return f"Warning: 'rm {target}' is not recoverable without backup."
    if cmd_name == "mv" and len(parts) >= 3:
        src, dst = parts[-2], parts[-1]
        return f"mv {dst} {src}"
    if cmd_name == "cp" and len(parts) >= 3:
        dst = parts[-1]
        return f"rm {dst}"
    return f"No inverse operation known for '{cmd}'."

def main():
    parser = argparse.ArgumentParser(description="Command history utility")
    parser.add_argument("--list", type=int, nargs="?", const=10, default=10, help="List recent N commands")
    parser.add_argument("--search", type=str, help="Search history by keyword")
    parser.add_argument("--undo", type=str, help="Suggest undo for given command")
    parser.add_argument("--log", type=str, nargs="?", const="", default=None, help="Log a command")
    parser.add_argument("--exit-code", type=int, default=0, help="Exit code for --log")
    args = parser.parse_args()
    if args.log is not None:
        entry = log_command(args.log, args.exit_code)
        print(json.dumps(entry))
    elif args.undo:
        print(suggest_undo(args.undo))
    elif args.search:
        results = search_history(args.search)
        for e in results:
            print(json.dumps(e))
    else:
        results = list_recent(args.list)
        for e in results:
            print(json.dumps(e))

if __name__ == "__main__":
    main()
