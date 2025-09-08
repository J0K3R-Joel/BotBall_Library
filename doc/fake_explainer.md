# FakeR Class Explainer

- **Author:** Joel Kalkusch

- **Email:** [kalkusch.joel@gmail.com](mailto:kalkusch.joel@gmail.com)

- **Creation Date:** 2025-07-28

---------

## Overview

The `FakeR` class is a robust utility designed for robotics projects to dynamically import, modify, and execute a `main()` function from another directory. It allows for seamless integration with communication modules, pause/resume event handling, and code adaptation without manually changing the source.

Key capabilities:

- Import and manipulate external `main.py` files.

- Automatically insert markers for pause events and threading.

- Replace sensitive constructs (e.g., `threading.Event()`) with placeholders.

- Execute `main()` in a thread if communication is required.

---

## Requirements

- Python 3.7+

- Custom modules:
  
  - `logger`
  
  - `fileR`
  
  - `RoboComm` (for `RobotCommunicator`)

- Standard libraries: `subprocess`, `ast`, `re`, `inspect`, `importlib`, `threading`

---

## Constructor

```python
FakeR(thread_instance: Event = None, comm_instance: RobotCommunicator = None)
```

**Args:**

- `thread_instance`: Optional `threading.Event` instance for pause/resume handling.

- `comm_instance`: Optional `RobotCommunicator` instance for robot communication.

**Behavior:**

- Initializes working and target directories.

- Sets internal flags (`comm_wanted`, `fake_main`, `kipr_module_name`).

- Automatically calls `setup()` to prepare the `main()` function.

---

## Instance Management Methods

### `set_instance_thread(Instance_thread: Event) -> None`

Set or overwrite the thread instance used for pause/resume.

### `set_instance_comm(communication_instance: RobotCommunicator) -> None`

Set or overwrite the communication instance.

### `check_instance_thread() -> bool`

Validates that a thread instance exists and is of type `Event`. Raises an exception if not.

### `check_instance_comm() -> bool`

Validates that a communication instance exists and is of type `RobotCommunicator`. Raises an exception if not.

---

## Private Utility Methods

These methods are internal helpers to manipulate code, handle imports, and manage execution.

### `__late_import()`

- Dynamically imports `main.py` from the `target_dir` and stores a reference to its `main()` function.

### `__insert_valid_markers_in_file(file_path: str) -> None`

- Analyzes the `main()` function AST.

- Inserts pause/event markers in the correct positions inside the `try` block.

### `__insert_beginning_in_code(code_str: str) -> str`

- Inserts predefined code lines at the start of the `try` block in `main()` (e.g., `console_clear()`).

### `__import_main_from_path(path_to_main_py: str)`

- Imports a module from a given path using `importlib.util` and returns it.

### `__extract_params_and_assign(method) -> list`

- Extracts parameters from a function's signature (excluding `self`).

- Assigns `None` as instance attributes for each parameter.

### `__replace_first_valid_event_assignment(code: str) -> str`

- Searches for `threading.Event()` assignments and replaces the first occurrence with `None`.

### `__resolve_import_alias(module_name: str, class_name: str, code: str) -> List[Optional[str]]`

- Determines how a module/class is imported (with alias, without alias, or missing).

- Returns metadata about the import.

---

## Public Methods

### `replace_exact_word(text: str, target: str, replacement: str) -> str`

Replaces all exact matches of `target` with `replacement` in the given text.

### `setup() -> None`

- Copies `main.py` from `working_dir` to `target_dir`.

- Modifies `main.py` to include pause/event markers and prepare it for communication.

- Imports the modified `main()` function.

- Determines if communication is required (`comm_wanted`).

### `get_current_path() -> str`

- Returns the current working directory (not actively used in main workflow).

### `start() -> None`

- Executes the prepared `main()` function.

- If communication is required, runs `main()` in a thread with `(thread_instance, comm_instance)`.

- Otherwise executes `main()` directly.

---

## Example Usage

This demonstrates a realistic usage scenario with WiFi, communication, and `FakeR`.

```python
from logger import log  # selfmade

try:
    import _kipr as k
    import time
    import threading
    import subprocess
    from commU import WifiConnector  # selfmade
    from RoboComm import RobotCommunicator  # selfmade
    from fake import FakeR  # selfmade
except Exception as e:
    log(f'Import Exception: {str(e)}', important=True, in_exception=True)


# ======================== VARIABLE DECLARATION =======================
# ===== GLOBAL VARIABLES =====
wifi = None
comm = None
pause_event = threading.Event()



# ======================== SETUP FUNCTIONS =======================
def Wifi_Setup():
    global wifi
    try:
        wifi = WifiConnector.standard_conf()
        print('IP Address is:', wifi.get_ip_address(), flush=True)
    except Exception as e:
        log(f'WIFI Exception: {str(e)}', important=True, in_exception=True)


def Comm_Setup(p_event, Communication_instance):
    global comm
    try:
        if Communication_instance == None:
            comm = RobotCommunicator('192.168.0.10', 10000, is_server=True) # one has to be the server, the other one has to be is_server=False (or be left out) -> both need the IP-Adress (IP from the the server) and the same port to communicate
            pause_event.set()
        else:
            Communication_instance.set_pause_event_instance(p_event)
    except Exception as e:
        log(f'Communication Exception: {str(e)}', important=True, in_exception=True)

def fake_main_setup():  # see this as the call of the main function -> only execute this in the if __name__ == "__main__": line (if you want communication)
    try:
        Comm_Setup(pause_event, comm)
        f_main = FakeR(thread_instance=pause_event, comm_instance  = comm)
        f_main.start()
    except Exception as e:
        log(str(e), important=True, in_exception=True)


def setup(pause_instance, Communication_instance):
    try:
        Wifi_Setup()  # you can delete this line from now on, just as the function!
        Comm_Setup(pause_instance, Communication_instance)

    except Exception as e:
        log(f'Setup Exception: {str(e)}', important=True, in_exception=True)


# ======================== IMPORTANT FUNCTIONS =======================
def end_main(communication_instance):
    communication_instance.disconnect()  
    log('PROGRAM FINISHED')

# ======================== CUSTOM METHODS =======================

def is_it_pressed():
    log('waiting till its pressed')
    while not TestButton.is_pressed():
        continue

def handle_high_priority(msg):
    try:
        log(f'HIGH PRIORITY MESSAGE RECEIVED: {msg}')
        is_it_pressed()
        log('continue with program...')
    except Exception as e:
        log(f'handle exception: {str(e)}', important=True, in_exception=True)

def do_something():
    log('driving straight...')
    time.sleep(1)
    log('turning...')
    time.sleep(1)

def another_main():
    log('breathing...')
    time.sleep(1)
    log('exhaling...')
    time.sleep(1)


# ======================== MAIN =======================

def main(p_event, communication):  # leave it as it is, just write in the try / catch block! Do not remove the "p_event" or "communication"! (You can obviously write anything outside and inside the main though) If you delete any of those parameters, there wont be a communication
    try:  # try / catch is always useful in the main! leave it!
        communication.on_new_main(another_main)  # if something does not working accordingly you can all the time send a message so another main will be executed
        setup(p_event, communication)  # if you use the ocmmunication, you need these instances
        communication.on_high_priority(handle_high_priority)
        print(TestButton.is_pressed(), flush=True)
        log('actual program running right now...')
        for _ in range(5):  # simulation of doing anything before sending a high priority message
            do_something()
        communication.send('hallo client!', priority='high')  # keep care that the client is running at this time as well, otherwise the message will get sent into the void
        for _ in range(5):
            do_something()

    except Exception as e:
        log(f'Main Exception: {str(e)}', important=True, in_exception=True)
    finally:
        end_main(communication)  # very important, you need to tell the main when to end (its important for communication, so if you do not need communication, you can remove this)


if __name__ == "__main__":
    try:
        fake_main_setup()  
    except Exception as e:
        log(str(e), important=True, in_exception=True)
```

### Notes

- The `main()` function in your project **must have the `try` block** and accept parameters `(p_event, communication)` for correct integration.

- `FakeR` automatically detects if communication is needed based on the number of `main()` parameters.

- `start()` will execute the real `main()` from your project; it will **not block unnecessarily** as long as `main()` exists.

- High-priority message handling and event pausing can be implemented in `main()` and connected functions.

---

## Typical Workflow

1. Instantiate `FakeR` with thread and communication instances.

2. `setup()` prepares the `main.py` function for execution (automatic during initialization).

3. Call `start()` to run the actual `main()` function in the correct mode (threaded if communication is used).

---

## Why & How?

It may come at your own interest to know why this class is so important. This class is espacially important, when you want communication, but not in the classical sense. you can use the [Communication](./RoboComm_explainer.md) class on its own and you will be fine. If you want to use the send messages with the priorities `high` or `new_main` it is essential though. This is due the following "problem" in python: There is no way of pausing a main and (while the pause is accuring) execute another function during the execution. Sometimes you want to pause on any given moment though, because if for example you know that something is wrong, you can tell the other robot with a `high` or `new_main` priority message that it should help, do another task, do from now on everything different,....  

---

## Conclusion

The `FakeR` class allows you to run your robot’s main code in a controlled, instrumented environment with full support for communication and pause events. By modifying `main()` on-the-fly, it ensures smooth integration with WiFi, high-priority messages, and other runtime features.
