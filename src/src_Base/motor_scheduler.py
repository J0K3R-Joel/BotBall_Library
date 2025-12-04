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
    from collections import deque
    from stop_manager import stop_manager
except Exception as e:
    log(f'Import Exception: {str(e)}', important=True, in_exception=True)

class MotorScheduler:
    AUTO_STOP_TIMEOUT = 1  # 50ms

    def __init__(self):
        self._lock = threading.RLock()
        self._old_lock = threading.Lock()
        self._commands = {}  # key=(port, func_id) -> dict(speed, thread_id, last_update)
        self._old_funcs = set()
        self.last_tid = {}
        self.last_fid = {}
        self._running = True
        self._setup_loop()

    def _setup_loop(self):
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self):
        try:
            while self._running:
                now = time.time()
                with self._lock:
                    for key, data in list(self._commands.items()):
                        port = data['port']
                        fid = key[1]

                        with self._old_lock:
                            if fid in self._old_funcs:
                                continue

                        if now - data['last_update'] > self.AUTO_STOP_TIMEOUT:
                            if data['speed'] != 0:
                                print('motor to stop: ', port, flush=True)
                                self._stop_motor_internal(port)
                            continue

                        k.mav(port, data['speed'])
                k.msleep(1)
        except Exception as e:
            log(str(e), in_exception=True)

    def set_speed(self, port, speed, func_id):
        try:
            key = (port, func_id)
            with self._lock:
                with self._old_lock:
                    if func_id in self._old_funcs:
                        return

                now = time.time()

                if key in self._commands:
                    self._commands[key].update({
                        'speed': speed,
                        'last_update': now
                    })
                    return

                to_remove = []
                for old_key in self._commands:
                    old_port, old_fid = old_key
                    if old_port == port and old_fid != func_id:
                        to_remove.append(old_key)
                for old_key in to_remove:
                    old_port, old_fid = old_key
                    with self._old_lock:
                        self._old_funcs.add(old_fid)
                    del self._commands[old_key]

                self._commands[key] = {
                    'port': port,
                    'speed': speed,
                    'last_update': now
                }

                self.last_fid[port] = func_id

                with self._old_lock:
                    if len(self._old_funcs) > 100:
                        self._old_funcs = set(list(self._old_funcs)[30:])
        except Exception as e:
            log(str(e), in_exception=True)

    def _stop_motor_internal(self, port):
        print(f'stopping motor int... {port}', flush=True)
        with self._lock:
            for key, data in list(self._commands.items()):
                if data['port'] == port:
                    data['speed'] = 0
                    break
        try:
            k.freeze(port)
        except Exception as e:
            log(str(e), in_exception=True)

    def stop_motor(self, port):
        print(f'stopping motor ext... {port}', flush=True)
        with self._lock:
            for key, data in list(self._commands.items()):
                if data['port'] == port:
                    with self._old_lock:
                        self._old_funcs.add(key[1])
                    del self._commands[key]
                    break
        try:
            k.freeze(port)
        except Exception as e:
            log(str(e), in_exception=True)

    def stop_all(self):
        print('hard stop.', flush=True)
        try:
            with self._lock:
                for key, data in list(self._commands.items()):
                    with self._old_lock:
                        self._old_funcs.add(data['func_id'])
                    k.freeze(data['port'])
                self._commands.clear()
        except Exception as e:
            log(str(e), in_exception=True)

    def shutdown(self):
        self._running = False


MOTOR_SCHEDULER = MotorScheduler()
