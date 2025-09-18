#!/usr/bin/python3
import os, sys
sys.path.append("/usr/lib")

from logger import *  # selfmade

# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com
# Notice: feel free to write me for questions or help!
# Date of creation: 2025-09-18

try:
    import threading
except Exception as e:
    log(f'Import Exception: {str(e)}', in_exception=True, important=True)


class StopManager:
    def __init__(self):
        self.motors = []
        self.servos = []
        self._lock = threading.Lock()

    def register_motor(self, motor):
        with self._lock:
            self.motors.append(motor)

    def register_servo(self, servo):
        with self._lock:
            self.servos.append(servo)

    def emergency_stop(self):
        with self._lock:
            motors_copy = list(self.motors)
            servos_copy = list(self.servos)

        for m in motors_copy:
            try:
                m.break_all_motors()
            except Exception as e:
                log(f"Error stopping motor: {e}", important=True, in_exception=True)

        for s in servos_copy:
            try:
                s._servo_disabler()
            except Exception as e:
                log(f"Error stopping servo: {e}", important=True, in_exception=True)
        log("Everything stopped!", important=True)

stop_manager = StopManager()
