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
    import inspect
    from stop_manager import stop_manager  # selfmade
except Exception as e:
    log(f'Import Exception: {str(e)}', important=True, in_exception=True)

class MotorScheduler:
    AUTO_STOP_TIMEOUT = 0.05  # 50ms
    AUTO_SHUTDOWN_TIMEOUT = 0.2  # 200ms

    def __init__(self):
        self._lock = threading.RLock()
        self._commands = {}
        self._old_funcs = set()
        self.last_fid = None
        self._running = True
        self.last_activity = None
        self._setup_loop()

    def _setup_loop(self):
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self):
        try:
            while self._running:
                now = time.time()
                with self._lock:
                    commands_copy = self._commands.copy()

                for key, data in list(commands_copy.items()):
                    port = data['port']
                    fid = key[1]

                    if fid in self._old_funcs:
                        continue

                    if now - data['last_update'] > self.AUTO_STOP_TIMEOUT or data['speed'] == 0:
                        if data['speed'] != 0:
                            self.stop_motor(port)
                        continue

                    k.mav(port, data['speed'])

                k.msleep(1)

            if time.time() - self.last_activity > self.AUTO_SHUTDOWN_TIMEOUT:
                self._running = False



        except Exception as e:
            log(str(e), in_exception=True)


    def set_speed(self, port, speed, func_id):
        if not self._running:
            self._setup_loop()

        try:
            with self._lock:
                if func_id in self._old_funcs:
                    return
                key = (port, func_id)
                now = time.time()
                self.last_activity = now

                if key in self._commands:
                    self._commands[key].update({
                        'speed': speed,
                        'last_update': now
                    })
                    return

                for old_key, data in list(self._commands.items()):
                    if data['port'] == port:
                        self.clear_list()
                        break

                self._commands[key] = {
                    'port': port,
                    'speed': speed,
                    'func_id': func_id,
                    'last_update': now
                }
        except Exception as e:
            log(str(e), in_exception=True)


    def stop_motor(self, port):
        with self._lock:
            for key, data in list(self._commands.items()):
                if data['port'] == port:
                    self._commands[key]['speed'] = 0
                    k.freeze(port)
                    break

    def stop_all(self):
        try:
            with self._lock:
                for key, data in list(self._commands.items()):
                    self._commands[key]['speed'] = 0
                    k.freeze(data['port'])
        except Exception as e:
            log(str(e), in_exception=True)

    def shutdown(self):
        self._running = False

    def clear_list(self):
        with self._lock:
            if len(self._commands) != 0:
                for old_key, data in list(self._commands.items()):
                    self._old_funcs.add(old_key[1])
                    break
                self._commands.clear()



MOTOR_SCHEDULER = MotorScheduler()
