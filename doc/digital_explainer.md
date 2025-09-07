# Digital Class – Explanation & Usage

- **Author:** Joel Kalkusch

- **Email:** [kalkusch.joel@gmail.com](mailto:kalkusch.joel@gmail.com)

- **Creation Date:** 2025-07-28

----------

## Overview

This document explains the usage of the `Digital` class, which provides a convenient interface for handling digital ports (such as buttons or sensors) using the KIPR framework. It covers method explanations, practical tips, and example use cases.

---

## Requirements

- Python 3

- KIPR framework (`_kipr` module)

- A logger function `log()` (from your `logger` module)

Import into your project:

```python
from digital import Digital
```

---

## Class

### Constructor

```python
d = Digital(port: int)
```

- **port (int):** The port number where the digital sensor (e.g., a button) is connected.

Internal attributes:

- `self.port`: Stores the port number.

- `self.last_state`: Last known state (0 = not pressed, 1 = pressed).

- `self.pressed_at`: Timestamp of when the button was pressed (or state tracking began).

- `self.state_timer`: State remembered when calling `time_begin()`.

---

## Methods

### 1. `current_value()`

```python
val = d.current_value()
```

- **Description:** Returns the current value of the digital port (0 or 1).

- **Return:** `int`
  
  - `0`: Not pressed
  
  - `1`: Pressed

---

### 2. `is_pressed()`

```python
pressed = d.is_pressed()
```

- **Description:** Checks if the button is currently pressed.

- **Return:** `bool`
  
  - `True`: Pressed
  
  - `False`: Not pressed

---

### 3. `state_changed()`

```python
changed = d.state_changed()
```

- **Description:** Detects whether the state of the button has changed since the last call.

- **How it works:** Compares the current state with the previously stored `last_state`.

- **Return:** `bool`
  
  - `True`: State has changed
  
  - `False`: State unchanged

> 💡 Tip: Useful for event-based programming when you only care about state transitions.

---

### 4. `time_begin()`

```python
d.time_begin()
```

- **Description:** Records the current state and timestamp.

- **Usage:** Call this method before measuring how long the button remains in a state.

- **Return:** `None`

> ⚠️ Important: Always call `time_begin()` before `time_end()`.

---

### 5. `time_end()`

```python
elapsed = d.time_end()
```

- **Description:** Returns how long the button has been in the state since `time_begin()` was called, but **only if the state has changed**.

- **Return:** `int` – Time in seconds.

- **Raises Exceptions:**
  
  - If `time_begin()` was not called before.
  
  - If the state has not changed since `time_begin()`.

Example:

```python
d.time_begin()
# Perform an action (press/release button)
print(d.time_end())  # Example: 2.35 seconds
```

---

## Typical Use Cases

### 1. Simple button check

```python
button = Digital(0)
if button.is_pressed():
    print("Button is pressed!")
```

### 2. Reacting to state changes

```python
button = Digital(0)
if button.state_changed():
    print("Button state has changed!")
```

### 3. Measuring how long a button was in a state

```python
button = Digital(0)
button.time_begin()

# Wait until the button changes state
while not button.state_changed():
    pass

print("Button remained in the same state for", button.time_end(), "seconds.")
```

---

## Tips

- **Robustness:** Use `try/except` in case `_kipr` fails to import.

- **Logging:** Errors are logged with `log()` for easier debugging.

- **Naming conventions:** The methods follow Pythonic style (e.g., `is_pressed`).

- **Avoid busy waiting:** Replace polling loops with event-driven mechanisms if possible.

---

## Conclusion

The `Digital` class encapsulates essential functionality for interacting with digital ports (e.g., buttons, sensors). It provides:

- Reading the current state

- Detecting state changes

- Measuring state durations
