# RobotCommunicator Class – Explanation & Usage

- **Author:** Joel Kalkusch

- **Email:** [kalkusch.joel@gmail.com](mailto:kalkusch.joel@gmail.com)

- **Creation Date:** 2025-07-28

---

## Overview

The `RobotCommunicator` class provides a TCP/IP-based communication interface between robots or between a robot and a client/server. It supports normal, high-priority, and experimental `new_main` messages, maintains message history, and allows callback functions on priority messages.

---

## Requirements

- Python 3

- `socket`, `threading`, `json`, `time` modules

- Logger function `log()` (from your `logger` module)

Import into your project:

```python
from robot_communicator import RobotCommunicator
```

---

## Class

### Constructor

```python
comm = RobotCommunicator(ip, port, is_server=False, pause_event=None)
```

- **Arguments:**
  
  - `ip` (str): IP address of the server.
  
  - `port` (int): TCP port to connect or bind.
  
  - `is_server` (bool): True if acting as server.
  
  - `pause_event` (threading.Event, optional): Event used to pause/resume main thread during high-priority messages.

Internal attributes:

- `self.sock`, `self.conn`: Socket connections.

- `self.connected`: Connection status flag.

- `self.all_messages`, `self.message_queue`: Store all received messages.

- `self.latest_message`, `self.new_message_flag`: Track latest messages.

- `self.position_history`: Stores position-priority messages.

- `self.high_priority_callback`, `self.new_main_callback`: Callback functions for special messages.

---

## Methods

### 1. Pause Event

- **Set pause event:**

```python
comm.set_pause_event_instance(threading.Event())
```

- **Check pause event:**

```python
comm.check_pause_event_instance()
```

> 💡 Tip: Ensure `pause_event` exists before using high-priority callbacks.

---

### 2. Sending Messages

```python
comm.send(message, priority='normal')
```

- **Arguments:**
  
  - `message` (any): Message to send.
  
  - `priority` (str): "normal" (default), "high", "pos", "new_main" (experimental).

- **Behavior:** Sends JSON-encoded messages via TCP.

- **High-priority:** Pauses main thread and executes callback.

- **Pos**: Saves the position, so the other one can see where it was last located

- **New-main:** Experimental; stops main thread and starts a new one.

---

### 3. Receiving Messages

- Automatic receive loop runs in a daemon thread.

- Stores messages in `message_queue` and `all_messages`.

- Calls `high_priority_callback` or `new_main_callback` if relevant.

- Position-priority messages are saved in `position_history`.

---

### 4. Message Access

- **Check for new message:**

```python
comm.has_new_message()
```

- **Get latest message:**

```python
msg = comm.get_latest()
```

- **Remove message:**

```python
comm.remove_message(msg)
```

- **Get saved messages:**

```python
queue = comm.get_safed_messages()
all_msgs = comm.get_all_messages()
```

---

### 5. Callbacks

- **High-priority callback:**

```python
comm.on_high_priority(callback_function)
```

- **New-main callback (experimental):**

```python
comm.on_new_main(callback_function)
```

> 💡 Tip: Use high-priority for interrupting main behavior safely; new-main is experimental.

---

### 6. Position Tracking

- **Get all positions:**

```python
comm.get_positions()
```

- **Get number of positions:**

```python
comm.get_position_len()
```

- **Get specific position:**

```python
comm.get_position_at(index)
```

> 💡 Tip: Useful for monitoring robot movement or path data.

---

### 7. Disconnect

```python
comm.disconnect()
```

- Safely closes socket connections and sets `self.connected` to False.

- Logs the disconnection process.

---

## Typical Use Cases

### 1. Establishing a client connection

```python
comm = RobotCommunicator('192.168.1.2', 5000)
```

### 2. Sending a normal message

```python
comm.send('Hello robot')
```

### 3. Registering a high-priority callback

```python
def emergency_stop(msg):
    print('High-priority message received:', msg)

comm.on_high_priority(emergency_stop)
```

### 4. Receiving and processing messages

```python
if comm.has_new_message():
    msg = comm.get_latest()
    print('Received:', msg)
```

### 5. Tracking positions

```python
positions = comm.get_positions()
print('All positions:', positions)
```

---

## Tips & Best Practices

- Ensure the IP and port are correct for client/server roles.

- Always check connection status before sending messages.

- Use high-priority callbacks for immediate response requirements.

- Be careful with `new_main` as it is experimental.

- Handle socket exceptions and disconnections gracefully.

---

## Conclusion

The `RobotCommunicator` class allows reliable TCP/IP messaging between robots with support for priority handling, message history, and callback execution. It is essential for:

- Robot-to-robot communication

- Real-time priority-based control

- Monitoring and tracking positional data
