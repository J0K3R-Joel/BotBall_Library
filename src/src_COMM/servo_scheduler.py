#!/usr/bin/python3
import os, sys
sys.path.append("/usr/lib")

from logger import *

try:
    import _kipr as k
    import threading
    import time
except Exception as e:
    log(f'ServoScheduler Import Exception: {str(e)}', important=True, in_exception=True)


class ServoScheduler:
    AUTO_DISABLE_TIMEOUT = 0.10

    def __init__(self):
        self._lock = threading.Lock()
        self._running = True

        self._commands = {}  # port: {pos, cmd_id, last_update, enabled}
        self._cmd_counter = 0

        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self):
        while self._running:
            now = time.time()

            with self._lock:
                for port, data in list(self._commands.items()):
                    pos = data["pos"]
                    last_update = data["last_update"]
                    enabled = data["enabled"]

                    if now - last_update > self.AUTO_DISABLE_TIMEOUT:
                        try:
                            k.disable_servo(port)
                        except Exception:
                            pass
                        data["enabled"] = False
                        continue

                    if not enabled:
                        try:
                            k.enable_servo(port)
                        except Exception:
                            pass
                        data["enabled"] = True

                    try:
                        k.set_servo_position(port, pos)
                    except Exception:
                        pass

            time.sleep(0.01)

    def set_position(self, port, pos):
        with self._lock:
            self._cmd_counter += 1
            cmd_id = self._cmd_counter

            self._commands[port] = {
                "pos": int(pos),
                "cmd_id": cmd_id,
                "last_update": time.time(),
                "enabled": self._commands.get(port, {}).get("enabled", False)
            }

            return cmd_id

    def disable_servo(self, port):
        with self._lock:
            try:
                k.disable_servo(port)
            except Exception:
                pass

            self._cmd_counter += 1
            self._commands[port] = {
                "pos": 0,
                "cmd_id": self._cmd_counter,
                "last_update": 0,
                "enabled": False
            }

    def disable_all(self):
        with self._lock:
            for port in list(self._commands.keys()):
                try:
                    k.disable_servo(port)
                except Exception:
                    pass
                self._commands[port]["enabled"] = False

SERVO_SCHEDULER = ServoScheduler()