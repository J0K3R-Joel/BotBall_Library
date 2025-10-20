# ServoX Class – Explanation & Usage

- **Author:** Joel Kalkusch

- **Email:** [kalkusch.joel@gmail.com](mailto:kalkusch.joel@gmail.com)

- **Creation Date:** 2025-09-15

---

## Overview

This document explains the usage of the `ServoX` class, which provides a higher-level abstraction for controlling servos on the Wombat/Wallaby robotics platform using the `_kipr` library. It simplifies enabling/disabling, position handling, and smooth movement transitions.

The class ensures that servo values stay within valid ranges and provides safety checks, logging, and motion utilities.

---

## Requirements

- Python 3

- KIPR `_kipr` library available (`import _kipr as k`)

- Custom `logger` module (for logging and error handling)

Import into your project:

```python
from servo import ServoX
```

---

## Class

### Constructor

```python
servo = ServoX(Port: int, maxValue: int = 2047, minValue: int = 0)
```

- **Port (int):** The servo port number.

- **maxValue (int, optional):** Maximum allowed servo value (default: 2047).

- **minValue (int, optional):** Minimum allowed servo value (default: 0).

Internal attributes:

- `self.port`: Target servo port.

- `self.max_value`: Upper limit for servo positions.

- `self.min_value`: Lower limit for servo positions.

---

## Methods

### 1. `_servo_enabler()`

```python
servo._servo_enabler()
```

- **Description:** Enables the servo port.

- **Note:** If a servo remains enabled, it will hold its current position. Useful for keeping an arm in place.

- **Return:** `None`

---

### 2. `_servo_disabler()`

```python
servo._servo_disabler()
```

- **Description:** Disables the servo port.

- **Return:** `None`

---

### 3. `_valid_range(value: int)`

```python
servo._valid_range(1000)
```

- **Description:** Checks if a given value is within the valid servo range.

- **Arguments:**
  
  - `value (int)`: Target position.

- **Return:** `bool` (`True` if valid, raises Exception otherwise)

---

### 4. `get_pos()`

```python
pos = servo.get_pos()
```

- **Description:** Reads the current servo position.

- **Return:** `int` (servo position)

---

### 5. `set_pos(value: int, enabler_needed: bool = True)`

```python
servo.set_pos(1500)
```

- **Description:** Sets the servo position, with optional automatic enabling/disabling.

- **Arguments:**
  
  - `value (int)`: Target position.
  
  - `enabler_needed (bool, optional)`: If `True`, the servo is enabled before and disabled after setting (default: `True`).

- **Return:** `None`

---

### 6. `add_to_pos(value: int, enabler_needed: bool = True)`

```python
servo.add_to_pos(-100)
```

- **Description:** Moves the servo relative to its current position.

- **Arguments:**
  
  - `value (int)`: Amount to add/subtract from the current position.
  
  - `enabler_needed (bool, optional)`: Same as in `set_pos`.

- **Return:** `None`

---

### 7. `range_to_pos(value: int, multi: int = 2, disabler_needed: bool = True)`

```python
servo.range_to_pos(1800, multi=3)
```

- **Description:** Smoothly moves the servo from its current position to the target value.

- **Arguments:**
  
  - `value (int)`: Target position.
  
  - `multi (int, optional)`: Speed factor (higher = faster but less smooth). Default: 2.
  
  - `disabler_needed (bool, optional)`: Whether to disable servo after movement. Default: `True`.

- **Return:** `None`

---

### 8. `range_from_to_pos(interval: list, multi: int = 2, disabler_needed: bool = True)`

```python
servo.range_from_to_pos([500, 1500], multi=2)
```

- **Description:** Smoothly moves the servo from one position to another, independent of its current position.

- **Arguments:**
  
  - `interval (list[int, int])`: Start and end positions.
  
  - `multi (int, optional)`: Speed factor (default: 2).
  
  - `disabler_needed (bool, optional)`: Whether to disable servo after movement. Default: `True`.

- **Return:** `None`

---

## Typical Use Cases

### 1. Simple positioning

```python
servo = ServoX(0) 
servo.set_pos(1200)
```

### 2. Relative movement

```python
servo = ServoX(1)
servo.add_to_pos(200)
```

### 3. Smooth transition

```python
servo = ServoX(2)
servo.range_to_pos(1800, multi=4)
```

### 4. Full interval movement

```python
servo = ServoX(3)
servo.range_from_to_pos([300, 1600], multi=3)
```

---

## Tips

- **Enabling/Disabling:** Leaving a servo enabled holds its position but consumes power. Disable when not needed.

- **Safety:** Always check servo ranges before testing new movements to avoid hardware stress.

- **Smooth motion:** Use higher `multi` values for faster (but jerkier) movements; use lower values for smoother control.

- **Error handling:** Wrap movement commands in `try/except` to handle out-of-range errors gracefully.

---

## Conclusion

The `ServoX` class provides safe and convenient methods to control servos on Wombat/Wallaby robots. It abstracts away low-level details of enabling, disabling, and checking ranges while adding motion utilities for both simple and smooth movements.

This makes it an essential utility for robotics projects requiring precise servo control.
