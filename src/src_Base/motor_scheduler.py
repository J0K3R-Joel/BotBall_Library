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
        self._commands_lock = threading.RLock()
        self._active_funcs = set()
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
                with self._commands_lock:
                    commands_copy = list(self._commands.items())

                stopped_ports = set()
                for (port, fid), data in commands_copy:
                    if self.last_fid.get(port) != fid:
                        continue

                    if now - data['last_update'] > self.AUTO_STOP_TIMEOUT and port not in stopped_ports:
                        stopped_ports.add(port)
                        self.stop_motor(port)
                        continue

                    # Motor ansteuern
                    try:
                        k.mav(port, data['speed'])
                    except Exception as e:
                        log(f"k.mav error for port={port}, fid={fid}: {e}", in_exception=True)

                k.msleep(1)
        except Exception as e:
            log(f"_loop Exception: {str(e)}", in_exception=True)

    def set_speed(self, port, speed, thread_id, func_id):
        with self._commands_lock:
            # Schon einmal ausgeführt? Dann abbrechen
            if func_id in self._old_funcs:
                return

            key = (port, func_id)

            # Clean start für diesen Port
            for old_key in list(self._commands.keys()):
                if old_key[0] == port:
                    self._old_funcs.add(old_key[1])
                    del self._commands[old_key]
                    try:
                        k.freeze(port)
                    except Exception as e:
                        log(f"freeze in set_speed Exception: {str(e)}", in_exception=True)
                    break

            # Neuen Command hinzufügen
            self._commands[key] = {
                'port': port,
                'speed': speed,
                'thread_id': thread_id,
                'last_update': time.time()
            }
            self.last_fid[port] = func_id
            self.last_tid[port] = thread_id

            # Overflow für alte Funktionen vermeiden
            if len(self._old_funcs) > 100:
                self._old_funcs = set(list(self._old_funcs)[-80:])

            print(f"new tid: {port} {thread_id} {func_id}", flush=True)

    def stop_motor(self, port):
        with self._commands_lock:
            keys_to_delete = [k for k, v in self._commands.items() if v['port'] == port]
            for key in keys_to_delete:
                self._old_funcs.add(key[1])
                del self._commands[key]

            self.last_fid.pop(port, None)
            self.last_tid.pop(port, None)

        try:
            k.freeze(port)
        except Exception as e:
            log(f"stop_motor Exception: {str(e)}", in_exception=True)

    def stop_all(self):
        print("hard stop.", flush=True)
        with self._commands_lock:
            for key, data in list(self._commands.items()):
                self._old_funcs.add(key[1])
                try:
                    k.freeze(data['port'])
                except Exception as e:
                    log(f"stop_all freeze Exception: {str(e)}", in_exception=True)
            self._commands.clear()
            self.last_fid.clear()
            self.last_tid.clear()

    def shutdown(self):
        self._running = False


MOTOR_SCHEDULER = MotorScheduler()
