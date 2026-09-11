# cmd-undo

A lightweight command-line history manager that logs executed shell commands to a local JSON file.

[![CI](https://github.com/cypherkeolis/cmd-undo/actions/workflows/ci.yml/badge.svg)](https://github.com/cypherkeolis/cmd-undo/actions)
[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/cypherkeolis/cmd-undo/releases)

## Description

`cmd-undo` is a minimal utility designed to track your shell command history. Unlike standard shell history which is often limited to simple text lines, `cmd-undo` stores structured data including timestamps. It provides a safety net by analyzing the last executed command to suggest a safe reverse operation (e.g., converting `mv a b` to `mv b a`) or issuing a warning for destructive commands like `rm`.

## Features

- **JSON Logging**: Stores command history in a human-readable `command_history.json` file.
- **Safe Undo**: Analyzes the last command to generate a reverse operation or a safety warning.
  - `mv a b` → `mv b a`
  - `mkdir dir` → `rmdir dir`
  - `rm file` → `WARNING: Cannot undo 'rm'...`
- **Keyword Search**: Quickly find previous commands by keyword.
- **Zero Dependencies**: Built entirely with the Python standard library.

## Installation and Usage

### Installation

No installation is required. Simply clone the repository and run the script directly with Python.

```bash
git clone https://github.com/cypherkeolis/cmd-undo.git
cd cmd-undo
```

### Usage

Run the main script to view the history, the last 5 commands, the suggested undo operation for the last command, and a search example:

```bash
python main.py
```

**Sample Output:**

```text
Command History Manager
========================================
Total commands logged: 4

Last 5 commands:
  [2024-01-01T10:00:00] rm old_file.txt
  [2024-01-01T10:05:00] mv a.txt b.txt
  [2024-01-01T10:10:00] mkdir new_dir
  [2024-01-01T10:15:00] cp source.txt backup.txt

Undo last command:
  WARNING: Cannot safely undo 'cp'. Consider removing 'backup.txt' if no longer needed.

Search for 'mv':
  [2024-01-01T10:05:00] mv a.txt b.txt
```

You can also import the module to use its functions programmatically:

```python
from main import log_command, undo_last_command, search_commands

# Log a new command
log_command("mv file1.txt file2.txt")

# Get the reverse operation for the last command
print(undo_last_command())  # Output: mv file2.txt file1.txt

# Search for commands containing 'file'
results = search_commands("file")
```

## Running the Tests

The project includes a test suite using `pytest`. To run the tests, ensure `pytest` is installed and execute:

```bash
pip install pytest
pytest
```

## License

This project is licensed under the MIT License.

```
MIT License

Copyright (c) 2024 cypherkeolis

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
