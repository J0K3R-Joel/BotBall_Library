# Logger Module Explainer

- **Author:** Joel Kalkusch

- **Email:** [kalkusch.joel@gmail.com](mailto:kalkusch.joel@gmail.com)

- **Creation Date:** 2025-07-28

--------

## Overview

This module provides a logging system that writes messages to a log file and optionally prints them to the console. It also manages log size and allows backups.

----

## Constants

- `LOG_FOLDER`: Directory where logs are stored (`//home//kipr`).

- `LOG_FILE`: Path to the main log file (`log_file.txt`).

---

## Main Functions

### `log(message: str, with_print: bool = True, important: bool = False, in_exception: bool = False) -> None`

Logs a message to the file and optionally prints it.

**Args:**

- `message` (str): Message to log.

- `with_print` (bool, optional): If `True`, prints the message to the console. Default is `True`.

- `important` (bool, optional): If `True`, surrounds the message with `====` for emphasis. Default is `False`.

- `in_exception` (bool, optional): If `True`, marks the log as an exception. Default is `False`.

**Returns:**

- None

**Behavior:**

- Determines the calling function and class.

- Formats the message with timestamp, location, and label.

- Writes the message to `LOG_FILE`.

- Optionally prints the message.

- Calls `__log_handler` to trim log file if necessary.

**Example:**

```python
log('System initialized')
log('Error connecting to WiFi', important=True, in_exception=True)
```

---

### `__log_handler(max_entries: int = 10000, trim_size: int = 500) -> None`

Ensures the log file does not exceed a specified number of entries.

**Args:**

- `max_entries` (int, optional): Maximum allowed log entries. Default is `10000`.

- `trim_size` (int, optional): Number of oldest entries to remove if exceeded. Default is `500`.

**Returns:**

- None

**Behavior:**

- Reads all lines from `LOG_FILE`.

- If the total exceeds `max_entries`, trims the oldest `trim_size` lines.

---

### `backup_log() -> None`

Creates a backup of the current log file.

**Args:**

- None

**Returns:**

- None

**Behavior:**

- Finds the next available backup file number.

- Copies all contents from `LOG_FILE` to a new backup file (`backup_log_file_X.txt`).

- Logs a successful backup message.

**Example:**

```python
backup_log()  # Creates a backup of the current log file
```

---

## Notes

- All log entries include timestamps and the source location (class and function).

- The `important` and `in_exception` flags help distinguish critical logs and exceptions.

- Backup files are automatically numbered to prevent overwriting.

- Ensure `LOG_FOLDER` exists and is writable by the running script.
