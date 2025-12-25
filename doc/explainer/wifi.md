# WifiConnector Class – Explanation & Usage

- **Author:** Joel Kalkusch

- **Email:** [kalkusch.joel@gmail.com](mailto:kalkusch.joel@gmail.com)

- **Creation Date:** 2025-07-28

----

## Overview

This document explains the usage of the `WifiConnector` class, which manages WiFi connections on the Wombat/Wallaby robotics platform using Linux networking tools (`nmcli`). It includes method explanations, best practices, and example use cases.

---

## Requirements

- Python 3

- Linux with `nmcli` installed (NetworkManager CLI)

- Custom modules: `logger`, `fileR`, `util`

Import into your project:

```python
from wifi_connector import WifiConnector
```

---

## Class

### Constructor

```python
wc = WifiConnector(ssid: str = None, password: str = None)
```

- **ssid (str):** Target WiFi network name.

- **password (str):** Password for the chosen WiFi network.

Internal attributes:

- `self.file_path`: Path to the WiFi mode configuration file.

- `self.AP_MODE`: String constant `'0'` for Access Point mode.

- `self.CLIENT_MODE`: String constant `'1'` for Client mode.

- `self.file_manager`: File manager object (`FileR`).

---

## Methods

### 1. `standard_conf()` (class method)

```python
wc = WifiConnector.standard_conf()
```

- **Description:** Creates a `WifiConnector` instance with a predefined SSID and password (Botball default).

- **Behavior:**
  
  - If not connected, enables WiFi scanning and tries to reconnect.
  
  - If connected, logs a success message.

- **Return:** A `WifiConnector` instance.

---

### 2. `get_mode()`

```python
mode = wc.get_mode()
```

- **Description:** Reads the current WiFi mode from the config file.

- **Return:** `str`
  
  - `'0'`: Access Point (AP) mode
  
  - `'1'`: Client mode
  
  - `'2'`: Event mode (not usable for WiFi communication)

---

### 3. `set_mode(new_mode: str)`

```python
wc.set_mode('1')
```

- **Description:** Sets the WiFi mode in the config file.

- **Arguments:**
  
  - `new_mode (str)`: `'0'`, `'1'`, or `'2'`.

- **Return:** `None`

---

### 4. `enable_wifi_scanning()`

```python
wc.enable_wifi_scanning()
```

- **Description:** Switches the device to client mode and performs a WiFi scan.

- **Return:** `None`

---

### 5. `list_available_networks()`

```python
wc.list_available_networks()
```

- **Description:** Lists all visible WiFi networks with SSID and signal strength.

- **Return:** `None` (prints results)

---

### 6. `is_connected_to_ssid()`

```python
connected = wc.is_connected_to_ssid()
```

- **Description:** Checks whether the device is currently connected to the configured SSID.

- **Return:** `bool`
  
  - `True`: Connected to target SSID
  
  - `False`: Connected to another SSID or not connected

---

### 7. `connect_to_wifi()`

```python
wc.connect_to_wifi()
```

- **Description:** Connects to the configured SSID with the configured password.

- **Raises Exception:** If `ssid` or `password` were not provided in the constructor.

- **Return:** `None`

---

### 8. `get_ip_address()`

```python
ip = wc.get_ip_address()
```

- **Description:** Retrieves the current IPv4 address of the device.

- **Return:** `str` (IP address)

---

### 9. `run()`

```python
wc.run()
```

- **Description:** Performs the full connection process:
  
  1. Ensures client mode is set.
  
  2. Connects to the WiFi if not already connected.
  
  3. Logs the current IP address.

- **Return:** `None`

---

## Typical Use Cases

### 1. Quick connect with defaults

```python
wc = WifiConnector.standard_conf()
```

### 2. Custom SSID and password

```python
wc = WifiConnector(ssid="MyWiFi", password="mypassword")
wc.run()
```

### 3. Scanning for available networks

```python
wc = WifiConnector()
wc.enable_wifi_scanning()
```

### 4. Checking connection state

```python
wc = WifiConnector(ssid="MyWiFi")
if wc.is_connected_to_ssid():
    print("Already connected!")
```

---

## Tips

- **Error handling:** Always wrap WiFi actions in `try/except` to handle connection issues.

- **Event mode:** Avoid setting mode to `'2'` (Event mode) as it disables WiFi.

- **Scanning:** Network scans may temporarily interrupt connections.

- **Security:** Do not hardcode SSIDs/passwords in production code – use secure storage.

---

## Conclusion

The `WifiConnector` class provides a robust abstraction for managing WiFi connections on Wombat/Wallaby robots. It allows you to:

- Switch between AP and Client modes

- Scan for available networks

- Connect to a WiFi network

- Retrieve the current IP address

This makes it an essential tool for robotics projects requiring wireless communication.
