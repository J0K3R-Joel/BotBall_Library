# Util Class – Explanation & Usage

- **Author:** Joel Kalkusch

- **Email:** [kalkusch.joel@gmail.com](mailto:kalkusch.joel@gmail.com)

- **Creation Date:** 2025-07-28

---

## Overview

This document explains the usage of the `Util` class, which provides a high-level interface for handling robot sensors (distance, light, button) and waiting behaviors in a robotics project. It describes the structure, available methods, and practical examples.

---

## Requirements

- Python 3

- KIPR framework (`_kipr` module)

- Logger function `log()` (from your `logger` module)

- Custom sensor classes: `Digital`, `LightSensor`, `DistanceSensor`

Import into your project:

```python
from util import Util
```

---

## Class

### Constructor

```python
util = Util(Instance_button_front_right=None, Instance_light_sensor_start=None, Instance_distance_sensor=None)
```

- **Arguments:**
  
  - `Instance_button_front_right`: Instance of `Digital` representing the front-right button.
  
  - `Instance_light_sensor_start`: Instance of `LightSensor` for detecting start light.
  
  - `Instance_distance_sensor`: Instance of `DistanceSensor` for measuring distances.

Internal attributes:

- `self.button_fr`: Stores the button instance.

- `self.light_sensor_start`: Stores the light sensor instance.

- `self.distance_sensor`: Stores the distance sensor instance.

- `self.isClose`: Flag used for distance checking.

---

## Methods

### 1. Setting Sensor Instances

- **Distance Sensor:**

```python
util.set_instance_distance_sensor(distance_sensor_instance)
```

- **Light Sensor:**

```python
util.set_instance_light_sensor_start(light_sensor_instance)
```

- **Button:**

```python
util.set_instance_button_fr(button_instance)
```

> 💡 Tip: Always initialize sensors before using other methods.

---

### 2. Checking Sensor Instances

- **Distance Sensor:**

```python
util.check_instance_distance_sensor()
```

- **Light Sensor:**

```python
util.check_instance_light_sensor_start()
```

- **Button:**

```python
util.check_instance_button_fr()
```

> 💡 Tip: Use these checks at the beginning of any method that interacts with sensors.

---

### 3. Waiting for Distance

```python
util.wait_til_distance_reached(mm_to_object, sideways=False)
```

- **Description:** Waits until an object is detected at the specified distance.

- **Args:**
  
  - `mm_to_object`: Desired distance in mm (10-800).
  
  - `sideways`: True if the robot moves sideways (mechanum wheels).

- **Returns:** `True` when target distance is reached.

> 💡 Tip: Calibrate the distance sensor properly for accurate readings.

---

### 4. Waiting for Movement

```python
util.wait_til_moved(waiting_millis, max_waiting_millis=8000)
```

- **Description:** Waits until the robot is slightly moved or touched.

- **Args:**
  
  - `waiting_millis`: Time to wait after movement.
  
  - `max_waiting_millis`: Maximum time allowed.

- **Returns:** None

> 💡 Tip: Make sure the robot is stationary before using this method.

---

### 5. Waiting for Light

```python
util.wait_for_light()
```

- **Description:** Waits until a light flash is detected.

- **Returns:** None

> 💡 Tip: Use `_kipr.wait_for_light()` if available for optimized behavior.

---

### 6. Waiting for Button Press

```python
util.wait_for_button()
```

- **Description:** Waits until the front-right button is pressed.

- **Returns:** None

> 💡 Tip: Add a small `time.sleep()` in loops to reduce CPU usage.

---

## Typical Use Cases

### 1. Waiting for an object to reach a specific distance

```python
util.wait_til_distance_reached(150)
```

### 2. Pausing until the robot is touched

```python
util.wait_til_moved(500)
```

### 3. Waiting for light to start

```python
util.wait_for_light()
```

### 4. Waiting for a button press

```python
util.wait_for_button()
```

---

## Tips & Best Practices

- Always initialize sensors before usage.

- Use `check_instance_*` methods for safety.

- Calibrate distance sensors for accurate measurements.

- Avoid busy-wait loops without `time.sleep()` to prevent high CPU usage.

- Logging is crucial for debugging sensor interactions.

---

## Conclusion

The `Util` class provides a comprehensive interface for managing robot sensors and waiting behaviors. It is essential for:

- Detecting objects and their proximity

- Handling physical interactions

- Synchronizing robot actions with external triggers such as light or button presses
