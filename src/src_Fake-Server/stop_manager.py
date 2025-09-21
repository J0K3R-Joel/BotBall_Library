#!/usr/bin/python3
import os, sys

sys.path.append("/usr/lib")

from logger import *  # selfmade

try:
    import threading
    import shutil
except Exception as e:
    log(f'Import Exception: {str(e)}', in_exception=True, important=True)


class StopManager:
    def __init__(self):
        self.motors = []
        self.servos = []
        self._lock = threading.Lock()
        self.is_stopped = False
        
        try:
            result = subprocess.run(["pwd"], capture_output=True, text=True, check=True)
            current_dir = result.stdout.strip()
            self.working_dir = os.path.dirname(current_dir)
        except Exception as e:
            log(f"Error while fetching for directory: {e}", important=True, in_exception=True)
            self.working_dir = os.getcwd()

    def register_motor(self, motor):
        with self._lock:
            self.motors.append(motor)

    def register_servo(self, servo):
        with self._lock:
            self.servos.append(servo)

    def emergency_stop(self):
        for m in self.motors:
            try:
                m.break_all_motors(stop=True)
            except Exception as e:
                log(f"Error stopping motor: {e}", important=True, in_exception=True)

        for s in self.servos: 
            try:
                s._servo_disabler()
            except Exception as e:
                log(f"Error stopping servo: {e}", important=True, in_exception=True)
        self.is_stopped = True
        log("Everything stopped!", important=True)

    def check_stopped(self):
        return self.is_stopped

    def change_stopped(self, is_stopped:bool) -> None:
        self.is_stopped = is_stopped

    def sys_end(self):
        try:
            if os.path.exists(self.working_dir + '/src/__pycache__') and os.path.isdir(self.working_dir + '/src/__pycache__'):
                shutil.rmtree(self.working_dir + '/src/__pycache__')
            else:
                print(self.working_dir + '/src/__pycache__', flush=True)
        except Exception as e:
            log(f'Ending Exception: {str(e)}', important=True, in_exception=True)
        os._exit(0)



stop_manager = StopManager()
