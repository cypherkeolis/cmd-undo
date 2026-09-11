# cmd-undo

Lightweight command-line utility to log, search, and "undo" recent shell commands.

[![CI](https://github.com/cypherkeolis/cmd-undo/actions/workflows/ci.yml/badge.svg)](https://github.com/cypherkeolis/cmd-undo/actions)
[![Version](https://img.shields.io/badge/version-1.0.1-blue.svg)](https://github.com/cypherkeolis/cmd-undo/releases)

`cmd-undo` is a zero-dependency Python tool that tracks your last 50 executed shell commands, storing them in a local JSONL file with timestamps and exit codes. It provides a simple CLI to review history, search for specific commands, and suggest inverse operations for common destructive commands like `rm` or `mv`.

## Features

- **Local History Logging**: Stores the last 50 commands in `.cmd_history.jsonl` (JSON Lines format).
- **Zero Dependencies**: Uses only the Python standard library (`json`, `os`, `subprocess`, `argparse`, `datetime`, `shlex`).
- **Command Search**: Quickly find past commands by keyword.
- **Undo Suggestions**:
  - Suggests `git checkout -- <file>` for `rm` commands if inside a Git repository.
  - Suggests `mv <dst> <src>` for `mv` commands.
  - Suggests `rm <dst>` for `cp` commands.
  - Warns if a command is not recoverable.
- **No Network Access**: All operations are local and offline.

## Installation

No installation required. The tool is a single Python script.

```bash
# Clone the repository
git clone https://github.com/cypherkeolis/cmd-undo.git
cd cmd-undo
```

## Usage

### Log a Command

Log a command with its exit code:

```bash
python main.py --log "rm file.txt" --exit-code 0
```

### List Recent Commands

List the last 10 commands (default):

```bash
python main.py --list
```

List the last 5 commands:

```bash
python main.py --list 5
```

### Search History

Search for commands containing a keyword:

```bash
python main.py --search "git"
```

### Suggest Undo

Get an undo suggestion for a specific command:

```bash
python main.py --undo "rm file.txt"
```

Example outputs:
- If in a Git repo: `git checkout -- file.txt`
- If not in a Git repo: `Warning: 'rm file.txt' is not recoverable without backup.`
- For `mv src dst`: `mv dst src`

## Running the Tests

The project includes a test suite using `pytest`.

```bash
# Install pytest if not already installed
pip install pytest

# Run tests
pytest
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
