# DistanceSensor Class – Explanation & Usage

- **Author:** Joel Kalkusch

- **Email:** [kalkusch.joel@gmail.com](mailto:kalkusch.joel@gmail.com)

- **Creation Date:** 2025-07-28

----------

## Overview

This document explains the usage of the `DistanceSensor` class, which provides a simple interface for handling analog distance sensors using the KIPR framework. It describes the structure, available methods, and practical examples.

---

## Requirements

- Python 3

- KIPR framework (`_kipr` module)

- A logger function `log()` (from your `logger` module)

Import into your project:

```python
from distance_sensor import DistanceSensor
```

---

## Class

### Constructor

```python
ds = DistanceSensor(port: int)
```

- **port (int):** The analog port where the distance sensor is connected.

Internal attributes:

- `self.port`: Stores the port number.

---

## Methods

### 1. `current_value()`

```python
val = ds.current_value()
```

- **Description:** Reads and returns the current analog value of the connected distance sensor.

- **Return:** `int`
  
  - The raw analog value measured on the specified port.

> 💡 Note: The exact range depends on your hardware. Often, higher values mean “closer object,” but this may vary between sensors.

---

## Typical Use Cases

### 1. Reading the distance sensor value

```python
sensor = DistanceSensor(0)
print("Current distance sensor value:", sensor.current_value())
```

### 2. Using sensor values in control logic

```python
sensor = DistanceSensor(0)

while True:
    value = sensor.current_value()
    if value > 2900:
        print("Object is very close!")
    elif value > 1500:
        print("Object is at medium distance.")
    else:
        print("No object nearby.")
    time.sleep(0.5)
```

---

## Tips

- **Calibration:** Raw analog values differ between sensor models. Perform calibration to map values into real-world distances.

- **Filtering:** Sensor readings may fluctuate. Use smoothing techniques (e.g., moving averages) for more stable results.

- **Performance:** Avoid overly frequent polling – introduce short delays with `time.sleep()` to reduce CPU load.

---

## Conclusion

The `DistanceSensor` class provides a straightforward way to read values from an analog distance sensor. While simple, it forms the foundation for:

- Detecting objects

- Building collision-avoidance systems

- Measuring proximity in robotics projects.
