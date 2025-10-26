#!/usr/bin/python3
import os, sys

sys.path.append("/usr/lib")

from logger import *  # selfmade

try:
    import threading
    import shutil
    import subprocess
except Exception as e:
    log(f'Import Exception: {str(e)}', in_exception=True, important=True)


class StopManager:
    def __init__(self):
        self.motors = []
        self.servos = []
        self._lock = threading.Lock()
        self.is_stopped = False
        self.driver_classes = []
        self.servo_classes = []
        
        try:
            result = subprocess.run(["pwd"], capture_output=True, text=True, check=True)
            current_dir = result.stdout.strip()
            self.working_dir = os.path.dirname(current_dir)
        except Exception as e:
            log(f"Error while fetching for directory: {e}", important=True, in_exception=True)
            self.working_dir = os.getcwd()

    # ======================== LAZY CLASS LOADING ========================
    def _load_driver_classes(self):
        '''
        lazy import of specific classes

        Args:
            None

        Returns:
            None
        '''
        import inspect, driveR
        self.driver_classes = [
            obj for name, obj in inspect.getmembers(driveR, inspect.isclass)
            if obj.__module__ == driveR.__name__
        ]

    def _load_servo_classes(self):
        '''
        lazy import of specific classes

        Args:
            None

        Returns:
            None
        '''
        from servo import ServoX
        self.servo_classes = [ServoX]

    # ======================== CHECK INSTANCES ========================

    def check_motor_instance(self, driver) -> None:
        '''
        Checks, if the wanted driver is a member of the driveR class

        Args:
            driver (driveR.{class) instance): the class that should be checked

        Returns:
            Either a TypeError if invalid or None
        '''
        if not self.driver_classes:
            self._load_driver_classes()

        if not isinstance(driver, tuple(self.driver_classes)):
            valid = [cls.__name__ for cls in self.driver_classes]
            log(f"{driver} is not a valid driveR-class. Valid: {valid}", important=True, in_exception=True)
            raise TypeError(f"{driver} is not a valid driveR-class. Valid: {valid}")


    def check_servo_instance(self, servox) -> None:
        '''
        Checks, if the wanted servo is a ServoX instance

        Args:
            servox (ServoX instance): the class that should be checked

        Returns:
            Either a TypeError if invalid or None
        '''
        if not self.servo_classes:
            self._load_servo_classes()

        if not isinstance(servox, tuple(self.servo_classes)):
            valid = [cls.__name__ for cls in self.servo_classes]
            log(f"{servox} is not a valid ServoX-class. Valid: {valid}", important=True, in_exception=True)
            raise TypeError(f"{servox} is not a valid ServoX-class. Valid: {valid}")


    # ======================== PUBLIC METHODS ========================
    def register_driver(self, driver) -> None:
        '''
        Let's you register a driveR class which has to stop if the emergency_stop() function gets executed

        Args:
            driver (driveR.{class) instance): the class which has to be registered

        Returns:
            None
        '''
        with self._lock:
            self.motors.append(driver)

    def register_servox(self, servox):
        '''
        Let's you register a servox class which has to stop if the emergency_stop() function gets executed

        Args:
            servox (ServoX.{class) instance): the class which has to be registered

        Returns:
            None
        '''
        self.check_servo_instance(servox)
        with self._lock:
            self.servos.append(servox)

    def emergency_stop(self):
        '''
        Stops all driveR and ServoX function from execution, if they are currently running

        Args:
            None

        Returns:
            None
        '''
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

    def check_stopped(self) -> bool:
        '''
        Let's you see if the emergency_stop() function was executed

        Args:
            None

        Returns:
            bool: If the emergency_stop() function was executed (True) or not (False)
        '''
        return self.is_stopped

    def change_stopped(self, is_stopped:bool) -> None:
        '''
        Let's you change the state of the stopper

        Args:
            is_stopped (bool): should it be stopped (True), or is it allowed to run (False)

        Returns:
            None
        '''
        self.is_stopped = is_stopped

    def sys_end(self):
        '''
        Removes the __pycache__ folder which gets created because of the FakeR class (setup() function). Also shuts down the entire program (use this function only, when everything is propperly shut off (like the camera, ...)

        Args:
            None

        Returns:
            None. Shuts down the program though
        '''
        try:
            if os.path.exists(self.working_dir + '/src/__pycache__') and os.path.isdir(self.working_dir + '/src/__pycache__'):
                shutil.rmtree(self.working_dir + '/src/__pycache__')
            else:
                print(self.working_dir + '/src/__pycache__', flush=True)
        except Exception as e:
            log(f'Ending Exception: {str(e)}', important=True, in_exception=True)
        os._exit(0)



stop_manager = StopManager()
