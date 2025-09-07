# FileR Class Explainer

- **Author:** Joel Kalkusch

- **Email:** [kalkusch.joel@gmail.com](mailto:kalkusch.joel@gmail.com)

- **Creation Date:** 2025-07-28

----------

## Overview

The `FileR` class is a simple utility for file operations such as reading, writing, and clearing files. It is designed to handle exceptions gracefully and log errors using a custom `log` function.

---

## Constructor

```python
FileR()
```

**Behavior:**

- Initializes a `FileR` instance. No parameters are required.

- Currently, the constructor does not perform any additional setup.

---

## Methods

### `reader(file_name: str) -> str`

Reads the entire content of a file.

**Args:**

- `file_name` (str): The path to the file to read.

**Returns:**

- The full content of the file as a string.

**Example:**

```python
file_manager = FileR()
content = file_manager.reader('/path/to/file.txt')
print(content)
```

### `writer(file_name: str, mode: str, msg: str) -> None`

Writes content to a file. Can be used to write, append, or modify content depending on the mode.

**Args:**

- `file_name` (str): The path to the file to write to.

- `mode` (str): The mode for opening the file (e.g., `'w'` for write, `'a'` for append).

- `msg` (str): The content to write into the file.

**Returns:**

- None

**Example:**

```python
file_manager.writer('/path/to/file.txt', 'w', 'Hello, World!')
```

### `cleaner(file_name: str) -> None`

Clears all content from a file.

**Args:**

- `file_name` (str): The path to the file to clear.

**Returns:**

- None

**Example:**

```python
file_manager.cleaner('/path/to/file.txt')  # File is now empty
```

---

## Notes

- All methods handle exceptions and log errors using the `log` function.

- Use appropriate file modes when writing (`'w'` for overwrite, `'a'` for append).

- The class is lightweight and intended for simple file operations in robotics projects or scripts where logging errors is essential.
