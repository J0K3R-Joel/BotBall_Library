#!/usr/bin/python3
import os, sys
sys.path.append("/usr/lib")

from logger import *

try:
    import _kipr as k
    import threading
    from collections import defaultdict
    import time
except Exception as e:
    log(f'ServoScheduler Import Exception: {str(e)}', important=True, in_exception=True)


class ServoScheduler:
    AUTO_STOP_TIMEOUT = 0.2  # 50ms  -> time after which the port will reduce it's speed to 0
    AUTO_SHUTDOWN_TIMEOUT = 0.2  # 200ms  - > time after which every motor immediately will shut off when no valid ID sent a new request (it will boot up automatically again, when there is a new command)
    TIME_RECOGNIZER = 0.05  # 500ms  -> time where a new tid will be created with the same thread id


    def __init__(self):
        self._lock = threading.RLock()
        self._running = True
        self.last_activity = None
        self._last_tid = None
        self._last_valid_tid = None
        self._all_tid = defaultdict(list)
        self._tid_counter = 0
        self.id_dict = {}
        self.id_set = set()
        self._commands = {}
        self._old_funcs = set()
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _setup_loop(self):
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _get_ID(self):
        tid = threading.current_thread().ident

        if self._last_valid_tid != tid and tid not in self.id_set and \
                (tid not in self.id_dict or time.time() - self.id_dict[tid] > self.TIME_RECOGNIZER):
            if tid not in self._all_tid:
                if len(self._all_tid[tid]) == 0 or self._all_tid[tid][-1] != self._tid_counter:  # does not exist yet
                    self._tid_counter += 1
                    self._all_tid[tid].append(self._tid_counter)
            elif self._all_tid[tid][-1] - 1 != self._all_tid[self._last_valid_tid][-1]:  # exists, but is not up-to-date
                self._tid_counter += 1
                self._all_tid[tid].append(self._tid_counter)

            if self._last_valid_tid in self.id_set:  # free the last tid from being blocked
                self.id_set.remove(self._last_valid_tid)
            self._last_valid_tid = tid
            self.id_set.add(self._last_tid)  # block last tid from entering this function

        self.id_dict[tid] = time.time()
        self._last_tid = tid
        return f'{tid}-{self._all_tid[tid][-1]}'

    def _loop(self):
        try:
            while self._running:
                now = time.time()
                with self._lock:
                    for key, data in list(self._commands.items()):
                        port = data['port']
                        fid = key[1]

                        if fid in self._old_funcs:
                            continue

                        if now - data['last_update'] > self.AUTO_STOP_TIMEOUT or not data['enabled']:
                            if data['enabled']:
                                self.disable_servo(port)
                            continue

                        self.enable_servo(port)
                        k.set_servo_position(port, data['pos'])
                        print(data['pos'], data['millis'])
                        k.msleep(data['millis'])


            if time.time() - self.last_activity > self.AUTO_SHUTDOWN_TIMEOUT:
                self.disable_all()
                self._running = False

        except Exception as e:
            log(str(e), in_exception=True)

    def set_position(self, port, pos):
        if not self._running:
            self._setup_loop()

        try:
            with self._lock:
                func_id = self._get_ID()
                if func_id in self._old_funcs:
                    return

                key = (port, func_id)
                now = time.time()
                self.last_activity = now
                millis = (abs(k.get_servo_position(port) - pos) / 10) + 20  # + 20 is just a kind of bias.
                self.enable_servo(port)

                if key in self._commands:
                    self._commands[key].update({
                        'pos': pos,
                        'millis': millis,
                        'last_update': now
                    })
                    return


                for old_key, data in list(self._commands.items()):
                    if data['port'] == port:
                        self.clear_list()
                        break

                self._commands[key] = {
                    'port': port,
                    'pos': pos,
                    'millis': millis,
                    'func_id': func_id,
                    'last_update': now
                }
                print(func_id, pos, k.get_servo_position(port), millis)
        except Exception as e:
            log(str(e), in_exception=True)

    def shutdown(self):
        self._running = False

    def enable_servo(self, port):
        with self._lock:
            for key, data in list(self._commands.items()):
                if data['port'] == port:
                    self._commands[key]['enabled'] = True
                    k.enable_servo(port)
                    break

    def disable_servo(self, port):
        with self._lock:
            for key, data in list(self._commands.items()):
                if data['port'] == port:
                    self._commands[key]['enabled'] = False
                    k.disable_servo(port)
                    break

    def disable_all(self):
        try:
            with self._lock:
                for key, data in list(self._commands.items()):
                    self._commands[key]['enabled'] = False
                    k.disable_servo(data['port'])
        except Exception as e:
            log(str(e), in_exception=True)

    def clear_list(self):
        with self._lock:
            if len(self._commands) != 0:
                for old_key, data in list(self._commands.items()):
                    self._old_funcs.add(old_key[1])
                    break
                self._commands.clear()

SERVO_SCHEDULER = ServoScheduler()