# LightSensor Class Explainer

- **Author:** Joel Kalkusch

- **Email:** [kalkusch.joel@gmail.com](mailto:kalkusch.joel@gmail.com)

- **Creation Date:** 2025-07-28

---

## Overview

The `LightSensor` class allows interaction with an analog light sensor. It provides methods to get the current sensor value, determine if the sensor sees black or white, and manage threshold calibration values.

---

## Constructor

```python
LightSensor(Port: int, value_white: int = None, value_black: int = None, bias: int = 500)
```

**Args:**

- `Port` (int): The analog port the sensor is connected to.

- `value_white` (int, optional): The sensor value representing white. Default is `None`.

- `value_black` (int, optional): The sensor value representing black. Default is `None`.

- `bias` (int, optional): Allowed margin of error for detection. Default is `500`.

**Behavior:**

- Initializes port, white/black calibration values, and bias.

---

## Getter Methods

### `get_value_black() -> int`

Returns the calibrated value representing black.

### `get_value_white() -> int`

Returns the calibrated value representing white.

### `get_bias() -> int`

Returns the allowed error margin (bias).

---

## Setter Methods

### `set_value_black(value: int) -> None`

Sets the value representing black.

### `set_value_white(value: int) -> None`

Sets the value representing white.

---

## Normal Methods

### `current_value() -> int`

Reads and returns the current analog value from the sensor port.

### `sees_Black() -> bool`

Returns `True` if the sensor detects black based on `val_white` and `bias`. Otherwise, `False`.

### `sees_White() -> bool`

Returns `True` if the sensor detects white based on `val_black` and `bias`. Otherwise, `False`.

---

## Example Usage

```python
sensor = LightSensor(Port=0, value_white=800, value_black=200, bias=50)

current = sensor.current_value()
print('Current sensor value:', current)

if sensor.sees_Black():
    print('Black detected')
elif sensor.sees_White():
    print('White detected')
else:
    print('Color not recognized')

# Adjust calibration
sensor.set_value_black(190)
sensor.set_value_white(810)
```

---

## Notes

- The `bias` allows for a margin of error, which helps account for sensor noise.

- Ensure `value_white` is higher than `value_black` for correct detection logic.

- Use `current_value()` for raw sensor readings and `sees_Black()` / `sees_White()` for boolean detection.
