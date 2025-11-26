#!/usr/bin/python3
import os, sys

sys.path.append("/usr/lib")

from logger import *

# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com
# Notice: feel free to write me for questions or help!
# Date of creation: 2025-11-26

try:
    import _kipr as k
    import threading
    import time
except Exception as e:
    log(f'Import Exception: {str(e)}', important=True, in_exception=True)


class MotorScheduler:
    AUTO_STOP_TIMEOUT = 0.05  # 50ms – same time as kipr does it

    def __init__(self):
        self._lock = threading.Lock()
        self._running = True

        self._commands = {}  # port: speed, cmd_id, last_update
        self._cmd_counter = 0

        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self):
        while self._running:
            now = time.time()

            with self._lock:
                for port, data in list(self._commands.items()):
                    speed = data["speed"]
                    last_update = data["last_update"]

                    if now - last_update > self.AUTO_STOP_TIMEOUT:
                        k.freeze(port)
                        continue

                    k.mav(port, speed)

            time.sleep(0.01)

    def set_speed(self, port, speed):
        with self._lock:
            self._cmd_counter += 1
            cmd_id = self._cmd_counter

            self._commands[port] = {
                "speed": speed,
                "cmd_id": cmd_id,
                "last_update": time.time()
            }

            return cmd_id

    def stop_motor(self, port):
        with self._lock:
            self._cmd_counter += 1
            k.freeze(port)
            self._commands[port] = {
                "speed": 0,
                "cmd_id": self._cmd_counter,
                "last_update": time.time()
            }

    def stop_all(self):
        with self._lock:
            self._cmd_counter += 1
            for port in self._commands:
                k.freeze(port)
                self._commands[port]["speed"] = 0
                self._commands[port]["last_update"] = time.time()

    def shutdown(self):
        self._running = False



MOTOR_SCHEDULER = MotorScheduler()
