# cmd-undo

A lightweight, zero-dependency CLI tool to log your last 10 shell commands and suggest inverse operations.

[![CI](https://github.com/cypherkeolis/cmd-undo/actions/workflows/ci.yml/badge.svg)](https://github.com/cypherkeolis/cmd-undo/actions)
[![Version](https://img.shields.io/badge/version-1.0.2-blue.svg)](https://github.com/cypherkeolis/cmd-undo/releases)

## Description

`cmd-undo` is a minimal utility designed to help developers keep track of recent shell activities. It stores the last 10 executed commands in a local JSON file and provides a simple interface to review this history. Additionally, it offers an "undo" feature that uses pattern matching to suggest inverse operations for common commands (e.g., suggesting `rmdir` for `mkdir` or `git reset` for `git commit`).

The tool relies entirely on the Python standard library, ensuring it runs anywhere Python is available without requiring `pip install` for third-party packages.

## Features

- **Local History Logging**: Automatically maintains a rolling log of the last 10 commands.
- **Inverse Command Suggestions**: Provides helpful counter-commands for common operations like `mkdir`, `rm`, `git commit`, and `git push`.
- **Zero Dependencies**: Uses only Python standard libraries (`json`, `os`, `sys`, `re`, `datetime`).
- **Lightweight**: Single-file implementation with no external configuration required.
- **JSON Storage**: History is stored in a human-readable `command_history.json` file.

## Installation

No installation is required. You can run the tool directly from the source code using Python 3.

```bash
# Clone the repository
git clone https://github.com/cypherkeolis/cmd-undo.git
cd cmd-undo
```

## Usage

The tool accepts three main subcommands: `log`, `list`, and `undo`.

### 1. Log a Command
Record a command to the history. This is typically done by aliasing or wrapping your shell prompt, but can also be used manually.

```bash
python3 main.py log "mkdir my_project"
# Output: Logged: mkdir my_project
```

### 2. List Recent History
Display the last 10 logged commands with their timestamps.

```bash
python3 main.py list
# Output:
# 1. [2023-10-27T10:00:00] mkdir my_project
# 2. [2023-10-27T10:01:00] cd my_project
# 3. [2023-10-27T10:02:00] git init
```

### 3. Suggest Undo
Check the last logged command and suggest an inverse operation if one is known.

```bash
python3 main.py undo
# Output:
# Last command: mkdir my_project
# Suggested inverse: rmdir
```

If no inverse is known for the last command, the tool will simply state that no suggestion is available.

## Running the Tests

The project includes a comprehensive test suite using `pytest`. To run the tests:

1. Ensure `pytest` is installed:
   ```bash
   pip install pytest
   ```

2. Run the test suite:
   ```bash
   python -m pytest
   ```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
