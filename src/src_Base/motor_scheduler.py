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
    from collections import defaultdict
    from stop_manager import stop_manager  # selfmade
except Exception as e:
    log(f'Import Exception: {str(e)}', important=True, in_exception=True)

class MotorScheduler:
    AUTO_STOP_TIMEOUT = 0.05  # 50ms  -> time after which the port will reduce it's speed to 0
    AUTO_SHUTDOWN_TIMEOUT = 0.2  # 200ms  - > time after which every motor immediately will shut off when no valid ID sent a new request (it will boot up automatically again, when there is a new command)
    TIME_RECOGNIZER = 0.5  # 500ms  -> time where a new tid will be created with the same thread id

    def __init__(self):
        self._lock = threading.RLock()
        self._commands = {}
        self._old_funcs = set()
        self._running = True
        self.last_activity = None
        self._last_tid = None
        self._last_valid_tid = None
        self._all_tid = defaultdict(list)
        self._tid_counter = 0
        self.id_dict = {}
        self.id_set = set()
        self._setup_loop()


    # ======================== PRIVATE METHODS ========================
    def _setup_loop(self):
        '''
        Starting function for the loop, so you can (re)create the loop at any time.

        Args:
            None

        Returns:
            None
        '''
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _get_ID(self) -> str:
        '''
        Creates an ID based of the current thread ID including a counter. The counter gets increased if the same thread is called again after some time (TIME_RECOGNIZER constant)

        Args:
            None

        Returns:
            str: ID consisting of {thread_id}-{counter_of_thread}
        '''
        try:
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
        except Exception as e:
            log(str(e), in_exception=True)

    def _loop(self) -> None:
        '''
        Loop which repeatedly calls a motor function but only if the ID is currently available and ignores every old ID. This makes it so only the latest command will get executed.

        Args:
            None

        Returns:
            None
        '''
        try:
            while self._running:
                now = time.time()
                with self._lock:
                    for key, data in list(self._commands.items()):
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

                        if self.last_activity and time.time() - self.last_activity > self.AUTO_SHUTDOWN_TIMEOUT:
                            self.shutdown()

        except Exception as e:
            log(str(e), in_exception=True)


    # ======================== PUBLIC METHODS =======================
    def set_speed(self, port: int, speed: int) -> None:
        '''
        Sets the speed of a motor. The newest call has priority, no matter which kind of Thread you are in.

        Args:
            port (int): the corresponding port of where the motor is plugged into
            speed (int): the speed the motor should go

        Returns:
            None
        '''
        try:
            with self._lock:
                func_id = self._get_ID()
                if func_id in self._old_funcs:
                    return

                if not self._running:
                    self._setup_loop()

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


    def stop_motor(self, port: int) -> None:
        '''
        Sets the speed to 0 of only this port and stops it immediately, so it will not move until the next call

        Args:
            port (int): the corresponding port of where the motor is plugged into

        Returns:
            None
        '''
        try:
            with self._lock:
                if threading.current_thread().ident not in self.id_set:
                    for key, data in list(self._commands.items()):
                        if data['port'] == port:
                            self.set_speed(data['port'], 0)  # delete this (?)
                            # self._commands[key]['speed'] = 0
                            k.freeze(port)
                            break
        except Exception as e:
            log(str(e))

    def stop_all(self) -> None:
        '''
        Sets the speed to 0 of every registered port and stops it immediately, so they will not move until the next call

        Args:
            None

        Returns:
            None
        '''
        try:
            with self._lock:
                if threading.current_thread().ident not in self.id_set:
                    for key, data in list(self._commands.items()):
                        self.set_speed(data['port'], 0)  # delete this (?) -> hard stop?
                        # self._commands[key]['speed'] = 0
                        k.freeze(data['port'])
        except Exception as e:
            log(str(e), in_exception=True)

    def shutdown(self) -> None:
        '''
        Let's you externally end the loop at any moment

        Args:
            None

        Returns:
            None
        '''
        self._running = False

    def clear_list(self) -> None:
        '''
        Let's you wipe out everything. Everything stops and you need to call everything again. This acts as a kind of emergency break.

        Args:
            None

        Returns:
            None
        '''
        try:
            with self._lock:
                if len(self._commands) != 0:
                    for old_key, data in list(self._commands.items()):
                        self._old_funcs.add(data['func_id'])
                    self._commands.clear()
                    self.shutdown()
        except Exception as e:
            log(str(e), in_exception=True)


MOTOR_SCHEDULER = MotorScheduler()
