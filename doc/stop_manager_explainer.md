# StopManager Class – Explanation & Usage

- **Author:** Joel Kalkusch

- **Email:** [kalkusch.joel@gmail.com](mailto:kalkusch.joel@gmail.com)

- **Creation Date:** 2025-09-21

---

## Overview

The `StopManager` class provides a central emergency-stop management system for robotics projects using `driveR` (motor drivers) and `ServoX` (servo abstraction).  

It allows registering drivers and servos, stopping all activity in case of an emergency, and cleaning up system resources. The class ensures safe shutdowns, proper thread handling, and reliable termination of active hardware components.

---

## Requirements

- Python 3

- Custom modules:
  
  - `logger` (logging & error handling)
  - `driveR` (self-made motor driver module)
  - `servo` (self-made `ServoX` class)

- Standard libraries: `os`, `sys`, `threading`, `inspect`, `shutil`, `subprocess`

Import into your project:

```python
from stop_manager import StopManager, stop_manager
```

---

### Class

### Constructor

```python
stop_manager = StopManager()
```

- **motors (list):** Registered motor driver instances.

- **servos (list):** Registered servo instances (ServoX).

- **_lock (threading.Lock):** Thread-safe lock for driver/servo registration.

- **is_stopped (bool):** Emergency stop state flag.

- **driver_classes (list):** All available classes from the driveR module.

- **working_dir (str):** Current working directory (fallback if pwd fails).

---

## Methods

### 1. `check_motor_instance(driver)`

```python
stop_manager.check_motor_instance(driver)
```

- **Description**: Validates if the given object is a proper driveR class instance.

- **Arguments**:
  
  - driver: Candidate object to check.

- **Return**: `None` (raises TypeError if invalid).

----

### 2. `register_driver(driver)`

```python
stop_manager.register_driver(driver_instance)
```

- **Description**: Registers a motor driver for emergency-stop handling.

- Arguments:
  
  - driver: Instance of a driveR class.

- Return: `None`

----

### 3. `register_servox(servox)`

```python
stop_manager.register_servox(servo_instance)
```

- **Description**: Registers a servo (ServoX) for emergency-stop handling.

- **Arguments**:
  
  - **servox**: Instance of ServoX.

- **Return**: `None` 

----

### 4. `emergency_stop()`

```python
stop_manager.emergency_stop()
```

- **Description**: Stops all registered motors and servos.

- **Details**:
  
  - Calls break_all_motors(stop=True) for each motor driver.
  
  - Calls _servo_disabler() for each registered servo.
  
  - Sets is_stopped = True.

- **Return**: `None`

----

### 5. `check_stopped()`

```python
stopped = stop_manager.check_stopped()
```

- **Description**: Checks if `emergency_stop()` was executed.

- **Return**: bool (True if stopped, False otherwise).

---

### 6. `change_stopped(is_stopped: bool)`

```python
stop_manager.change_stopped(True)
```

- **Description**: Manually sets the stopped state.

- **Arguments**:
  
  - `is_stopped`(bool): New state (True = stopped, False = active).

- **Return**: `None`

---

### 7. `sys_end()`

```python
stop_manager.sys_end()
```

- **Description**: Cleans up and shuts down the program.

- **Details**:
  
  - Removes __pycache__ folder (created by FakeR setup).
  
  - Exits the program using `os._exit(0)`.

- **Return**: `None` (terminates the process).

---

## Typical Use Cases

### 1. Registering a driver

```python
driver = driveR.MyMotorDriver()
stop_manager.register_driver(driver)
```

### 2. Registering a servo

```python
servo = ServoX(0)
stop_manager.register_servox(servo)
```

### 3. Triggering an emergency stop

```python
stop_manager.emergency_stop()
```

### 4. Checking if stopped

```python
if stop_manager.check_stopped():
    print("System is in emergency stop mode")
```

### 5. System shutdown

```python
stop_manager.sys_end()
```

---

## Tips

- **Thread safety**: Use provided `register_driver` and `register_servox` methods instead of directly modifying lists.

- **Emergency behavior**: Always register drivers/servos at program startup so they can be stopped safely.

- **Logging**: All errors and events are passed through the custom logger for debugging.

- **Shutdown sequence**: Call `sys_end()` only after all devices (e.g., cameras, sensors) have been safely stopped. Typically you do not even need to call it (especially when you are using communication)

---

## Conclusion

The StopManager class centralizes emergency-stop logic for both motor drivers and servos. By registering components, it ensures that all critical hardware can be halted quickly and consistently in case of errors or safety events.

It provides essential infrastructure for robotics projects requiring robust emergency handling and clean system shutdowns.
