# cmd-undo

A lightweight Python CLI tool that logs executed shell commands to a local JSON file and provides an 'undo' command that suggests or executes the inverse operation for common commands.

[![CI](https://github.com/cypherkeolis/cmd-undo/actions/workflows/ci.yml/badge.svg)](https://github.com/cypherkeolis/cmd-undo/actions)
[![Version](https://img.shields.io/badge/version-1.0.3-blue.svg)](https://github.com/cypherkeolis/cmd-undo/releases)

## Description

`cmd-undo` acts as a safety net for your terminal sessions. It tracks a history of commands you execute and allows you to "undo" the last action by mapping common destructive or state-changing commands to their logical inverses. It relies entirely on the Python standard library, making it easy to install and audit.

## Features

- **Command Logging**: Automatically appends executed commands to a local `command_log.json` file.
- **Inverse Detection**: Maps common commands to their reverses:
  - `rm` → `git checkout --`
  - `mkdir` → `rmdir`
  - `cp` → `mv` (move destination back to source)
  - `mv` → `mv` (swap source and destination)
  - `touch` → `rm`
- **Safe Execution**: Uses `subprocess` to execute inverse commands with error handling.
- **Zero Dependencies**: Built using only the Python standard library (`json`, `os`, `subprocess`, `sys`).

## Installation

Since this project uses only the standard library, you only need Python 3.6+ installed.

```bash
git clone https://github.com/cypherkeolis/cmd-undo.git
cd cmd-undo
```

## Usage

Run the main script to see the logging and undo logic in action:

```bash
python main.py
```

The script will:
1. Log a sequence of sample commands (`mkdir`, `touch`, `rm`).
2. Identify the inverse of the last command (`rm` → `git checkout`).
3. Execute the inverse command.
4. Print the remaining logged commands.

## Running the Tests

The project includes a comprehensive test suite using `pytest`. To run the tests:

1. Install pytest if you haven't already:
   ```bash
   pip install pytest
   ```

2. Run the tests:
   ```bash
   pytest
   ```

## License

This project is licensed under the MIT License.

```
MIT License

Copyright (c) 2024 Cypher Keolis

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
