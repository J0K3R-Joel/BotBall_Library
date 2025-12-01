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
        self._lock = threading.Lock()
        self._commands = {}  # port -> dict(speed, thread_id, func_id, last_update)
        self._old_funcs = set()
        self.last_tid = {}
        self.last_fid = {}
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
                    commands_copy = list(self._commands.items())

                stopped_ports = set()

                for key, data in commands_copy:
                    port = data['port']
                    fid = data['func_id']

                    if self.last_fid.get(port) != fid:
                        continue

                    if now - data['last_update'] > self.AUTO_STOP_TIMEOUT and port not in stopped_ports:
                        stopped_ports.add(port)
                        self.stop_motor(port)
                        continue

                    try:
                        if self.last_fid.get(port) == data['func_id']:
                            k.mav(port, data['speed'])
                    except Exception as e:
                        log(f"k.mav error for fid={fid}, port={port}: {str(e)}", in_exception=True)

                k.msleep(1)
        except Exception as e:
            log(str(e), in_exception=True)

    def set_speed(self, port, speed, thread_id, func_id):
        try:
            with self._lock:
                if func_id in self._old_funcs:
                    return

                key = (port, func_id)
                now = time.time()

                if key in self._commands:
                    self._commands[key].update({
                        'speed': speed,
                        'thread_id': thread_id,
                        'last_update': now
                    })
                    self.last_fid[port] = func_id
                    self.last_tid[port] = thread_id
                    return

                for old_key, data in list(self._commands.items()):
                    if data['port'] == port:
                        self._old_funcs.add(data['func_id'])
                        del self._commands[old_key]
                        break

                self._commands[key] = {
                    'port': port,
                    'speed': speed,
                    'func_id': func_id,
                    'thread_id': thread_id,
                    'last_update': now
                }

                self.last_fid[port] = func_id
                self.last_tid[port] = thread_id
        except Exception as e:
            log(str(e), in_exception=True)

    def stop_motor(self, port):
        print(f"stopping motor {port}...", flush=True)
        with self._lock:
            keys_to_delete = [k for k, data in self._commands.items() if data['port'] == port]
            for key in keys_to_delete:
                del self._commands[key]
        try:
            k.freeze(port)
        except Exception as e:
            log(str(e), in_exception=True)

    def stop_all(self):
        print('hard stop.', flush=True)
        try:
            with self._lock:
                for key, data in list(self._commands.items()):
                    k.freeze(data['port'])
                self._commands.clear()
        except Exception as e:
            log(str(e), in_exception=True)

    def shutdown(self):
        self._running = False


MOTOR_SCHEDULER = MotorScheduler()
