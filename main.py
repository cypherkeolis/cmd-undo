import json
import os
import subprocess
import sys

LOG_FILE = "command_log.json"

def load_log():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as f:
            return json.load(f)
    return []

def save_log(log):
    with open(LOG_FILE, 'w') as f:
        json.dump(log, f, indent=2)

def log_command(cmd):
    log = load_log()
    log.append({"command": cmd})
    save_log(log)
    return cmd

def get_inverse(cmd):
    parts = cmd.split()
    if not parts:
        return None
    base = parts[0]
    if base == 'rm':
        return f"git checkout -- {' '.join(parts[1:])}"
    elif base == 'mkdir':
        return f"rmdir {' '.join(parts[1:])}"
    elif base == 'cp':
        if len(parts) >= 3:
            src, dst = parts[1], parts[2]
            return f"mv {dst} {src}"
    elif base == 'mv':
        if len(parts) >= 3:
            src, dst = parts[1], parts[2]
            return f"mv {dst} {src}"
    elif base == 'touch':
        return f"rm {' '.join(parts[1:])}"
    return None

def undo_last():
    log = load_log()
    if not log:
        return None
    last_cmd = log[-1]["command"]
    inverse = get_inverse(last_cmd)
    if inverse:
        log.pop()
        save_log(log)
        return inverse
    return None

def run_command(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False

if __name__ == '__main__':
    log_command("mkdir test_dir")
    log_command("touch test_dir/file.txt")
    log_command("rm test_dir/file.txt")
    inverse = undo_last()
    if inverse:
        print(f"Undo: {inverse}")
        run_command(inverse)
    log = load_log()
    print(f"Commands logged: {len(log)}")
