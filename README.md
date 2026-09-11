# cmd-undo

A lightweight, offline Python CLI tool for logging and replaying your last 5 shell commands.

[![CI](https://github.com/cypherkeolis/cmd-undo/actions/workflows/ci.yml/badge.svg)](https://github.com/cypherkeolis/cmd-undo/actions)
[![Version](https://img.shields.io/badge/version-1.0.4-blue.svg)](https://github.com/cypherkeolis/cmd-undo/releases)

## Description

`cmd-undo` provides a simple "undo" mechanism for terminal mistakes without requiring complex shell integration or external dependencies. It logs the last 5 executed commands, along with their exit codes and timestamps, to a local JSON file. You can view this history or retrieve the exact command string for any entry to copy-paste and re-execute.

## Features

- **Lightweight**: Pure Python standard library implementation. No external dependencies.
- **Local Storage**: Stores history in a local `command_history.json` file.
- **Limited History**: Automatically retains only the last 5 commands to keep the file small.
- **Metadata Tracking**: Records the command string, exit code, and ISO 8601 timestamp.
- **Replay Capability**: Retrieve the exact command string by index for easy copy-pasting.
- **Offline**: Works entirely locally; no network calls or cloud services required.

## Installation

No installation is required. You can run the script directly using Python 3.

```bash
# Clone the repository
git clone https://github.com/cypherkeolis/cmd-undo.git
cd cmd-undo
```

## Usage

The tool supports three main commands: `add`, `list`, and `replay`.

### 1. Add a Command
Log a command to the history. You can optionally specify the exit code.

```bash
python3 main.py add "ls -la" 0
python3 main.py add "git commit -m 'fix'" 1
```

### 2. List Recent History
View the last 5 recorded commands with their indices, timestamps, and exit codes.

```bash
python3 main.py list
# Output:
# [0] 2023-10-27T10:00:00 | exit=0 | ls -la
# [1] 2023-10-27T10:01:00 | exit=1 | git commit -m 'fix'
```

### 3. Replay a Command
Print the exact command string for a specific index. This allows you to copy-paste the command back into your terminal.

```bash
python3 main.py replay 0
# Output:
# ls -la
```

## Running the Tests

The project includes a test suite using `pytest`. To run the tests:

1. Ensure `pytest` is installed:
   ```bash
   pip install pytest
   ```

2. Run the tests:
   ```bash
   python -m pytest
   ```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
