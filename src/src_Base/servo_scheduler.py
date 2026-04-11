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
    AUTO_STOP_TIMEOUT = 0.3  # 50ms  -> time after which the port will reduce it's speed to 0
    AUTO_SHUTDOWN_TIMEOUT = 5  # 200ms  - > time after which every motor immediately will shut off when no valid ID sent a new request (it will boot up automatically again, when there is a new command)
    TIME_RECOGNIZER = 0.5  # 500ms  -> time when a new tid will be created with the same thread id

    def __init__(self):
        """
        Not for basic users! Schedules every servo that makes them threadsafe. Blocks old activities so only the newest calls can use the servo

        Args:
            None
        """
        self._lock = threading.RLock()
        self._running = False
        self.last_activity = None
        self._last_tid = None
        self._last_valid_tid = None
        self._all_tid = defaultdict(list)
        self._tid_counter = 0
        self.id_dict = {}
        self.id_set = set()
        self._commands = {}
        self._old_funcs = set()
        self._thread = threading.Thread(target=self._loop)

    def _setup_loop(self) -> None:
        """
        Start a new endless loop

        Args:
            None

        Returns:
            None
        """
        self._running = True
        k.enable_servo(0)
        k.enable_servo(1)
        k.enable_servo(2)
        k.enable_servo(3)
        self._thread = threading.Thread(target=self._loop)
        self._thread.start()

    def _get_ID(self) -> str:
        """
        Create an ID based on the thread and time of last call from the same thread

        Args:
            None

        Returns:
            str: The ID which got created
        """
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

    def _loop(self) -> None:
        """
        Loop which will automatically end if no further instruction of movement came

        Args:
            None

        Returns:
            None
        """
        try:
            while self._running:
                with self._lock:
                    for key, data in list(self._commands.items()):
                        fid = key[1]

                        if fid in self._old_funcs:
                            log('old', important=True)
                            continue

                        port = data['port']
                        enabled = data['enabled']
                        last_update = data['last_update']
                        to_sleep = data['millis']
                        pos = data['pos']
                        already_set = data['already_set']

                        # if time.time() - last_update > self.AUTO_STOP_TIMEOUT and enabled:
                        #     self.disable_servo(port)
                        #     continue
                        #log(f'{pos, port, to_sleep}')

                        if enabled and not already_set:
                            #log('here')
                            #self.enable_servo(port)
                            k.set_servo_position(port, pos)
                            k.msleep(to_sleep)
                            self.last_activity -= to_sleep/1000  # -> to_sleep is in milliseconds and you need to convert it into seconds
                            #self._commands.pop(key)
                            self._commands.update({
                                'already_set': True
                            })


                if self.last_activity and time.time() - self.last_activity > self.AUTO_SHUTDOWN_TIMEOUT:
                    print(time.time(), self.last_activity, time.time() - self.last_activity, flush=True)
                    #log('dead', important=True)
                    self.disable_all()
                    self._running = False

        except Exception as e:
            log(str(e), in_exception=True)

    def set_position(self, port: int, pos: int) -> bool:
        """
        Set the position of a servo

        Args:
            port (int): The port where the servo is plugged into
            pos (int): Where the servo should go

        Returns:
            bool: If the value is set (True) or if it is getting blocked from being set (False)
        """

        try:
            #with self._lock:
            func_id = self._get_ID()
            if func_id in self._old_funcs:
                log('old', important=True)
                return False

            if not self._running:
                self._setup_loop()

            key = (port, func_id)
            self.last_activity = time.time()

            millis = int((abs(k.get_servo_position(port) - pos))) # +20 to increase the time it is allowed to take.
            if millis == 0:
                millis = 1

            if key in self._commands:
                self._commands[key].update({
                    'pos': pos,
                    'millis': millis,
                    'last_update': self.last_activity,
                    'enabled': True,
                    'already_set': False
                })
                return True
            for old_key, data in list(self._commands.items()):
                if data['port'] == port:
                    log('old', important=True)
                    self._old_funcs.add(data['func_id'])
                    self.disable_all()
                    break

            self._commands[key] = {
                'port': port,
                'pos': pos,
                'millis': millis,
                'func_id': func_id,
                'enabled': True,
                'already_set': False,
                'last_update': self.last_activity
            }
            return True
        except Exception as e:
            log(str(e), in_exception=True)

    def enable_servo(self, port):
        """
        Enable one specific servo port

        Args:
            port (int): The port where the servo is plugged into

        Returns:
            None
        """
        log(f'enabled: {port}')
        try:
            with self._lock:
                for key, data in list(self._commands.items()):
                    if data['port'] == port:
                        self._commands[key]['enabled'] = True
                        k.enable_servo(port)
                        break
        except Exception as e:
            log(str(e), in_exception=True)

    def disable_servo(self, port: int) -> None:
        """
        Disable one specific servo port

        Args:
            port (int): The port where the servo is plugged into

        Returns:
            None
        """
        log('disabled', important=True)
        with self._lock:
            for key, data in list(self._commands.items()):
                if data['port'] == port:
                    self._commands[key]['enabled'] = False
                    k.disable_servo(port)
                    break

    def disable_all(self) -> None:
        """
        Disable all active servos

        Args:
            None

        Returns:
            None
        """
        try:
            log('disabled', important=True)
            with self._lock:
                for key, data in list(self._commands.items()):
                    self._commands[key]['enabled'] = False
                    k.disable_servo(data['port'])
        except Exception as e:
            log(str(e), in_exception=True)

    def clear_list(self) ->  None:
        """
        Removes all pending servo tasks and block the threads from execution

        Args:
            None

        Returns:
            None
        """
        with self._lock:
            if len(self._commands) != 0:
                self.shutdown()
                for old_key, data in list(self._commands.items()):
                    self._old_funcs.add(old_key[1])
                    k.disable_servo(data['port'])
                self._commands.clear()

    def shutdown(self) -> None:
        """
        Stop all executions that are about to happen

        Args:
            None

        Returns:
            None
        """
        with self._lock:
            self._running = False


SERVO_SCHEDULER = ServoScheduler()