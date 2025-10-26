#!/usr/bin/python3
import os, sys
sys.path.append("/usr/lib")

from logger import *  # selfmade

# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com
# Notice: feel free to write me for questions or help!
# Date of creation: 2025-09-15

try:
    import _kipr as k
    import threading
    import uuid
    from typing import Optional
    from stop_manager import stop_manager  # selfmade
except Exception as e:
    log(f'Import Exception in WifiConnector: {str(e)}', important=True, in_exception=True)

class ServoX:
    def __init__(self, Port: int, maxValue: int = 2047, minValue:int = 0):
        self.port = Port
        self.max_value = maxValue
        self.min_value = minValue
        self._servo_lock = threading.Lock()
        self._active_servo_id = None
        stop_manager.register_servox(self)

    # ======================== PRIVATE METHODS ========================
    def _manage_servo_stopper(self, beginning: bool) -> Optional[str]:
        '''
        Manages the Lock of every class method, so if it (for example) gets spun clockwise and counterclockwise at the same time, the one that was sent through high priority will get executed and the other one does not

        Args:
            beginning (bool): is it in the beginning of a function (True) or at the end of a function (False)

        Returns:
            str: the ID of the servo at this moment
        '''
        with self._servo_lock:
            if beginning:
                new_id = str(uuid.uuid4())
                self._active_servo_id = new_id
                return new_id
            else:
                self._active_servo_id = None
                return None

    def _is_servo_active(self, servo_id: str) -> bool:
        '''
        Validates if the servo ID is still the same

        Args:
            servo_id (str): the ID from the manager

        Returns:
            bool: Is it still valid (True), or not (False)
        '''
        with self._servo_lock:
            return self._active_servo_id == servo_id

    def _servo_enabler(self) -> None:
        '''
        Enables the servo port. Hint: If a servo is staying enabled, without being disabled, it stays at the place where it is at the moment. This is very useful if you use a servo for an arm

        Args:
            None

        Returns:
            None
        '''
        k.enable_servo(self.port)

    def _servo_disabler(self) -> None:
        '''
        Disables the servo port

        Args:
            None

        Returns:
            None
        '''
        self._manage_servo_stopper(False)
        k.disable_servo(self.port)

    def _valid_range(self, value:int) -> bool:
        '''
        Verifies, if the value is inside the min and max value of the servo

        Args:
            value (int): The number which should be checked if it is in the range

        Returns:
            bool: If it is a valid number (True), else it raises an exception
        '''
        in_range = self.min_value <= value <= self.max_value
        if not in_range:
            log(f"{value} is out of range, where the range is between {self.min_value} to {self.max_value}", important=True, in_exception=True)
            raise ValueError(f"{value} is out of range, where the range is between {self.min_value} to {self.max_value}")
        return in_range

    def _set_pos_internal(self, value: int, enabler_needed: bool=True) -> None:
        '''
        Sets the position of the servo internally without a Lock, so you need to manage them

        Args:
            value (int): the value where it has to be
            enabler_needed (bool, optional): If True (default), it enables and disables the servo port. If it is set to False, then the port will not move if you did not enabled it first

        Returns:
            None
        '''
        millis = (abs(self.get_pos() - value) / 100) + 20 # + 20 is just a kind of bias.
        print(millis, flush=True)
        if enabler_needed:
            self._servo_enabler()
        if self._valid_range(value):
            k.set_servo_position(self.port, int(value))
            k.msleep(int(millis))
        if enabler_needed:
            self._servo_disabler()

    # ======================== PUBLIC METHODS ========================
    def get_max_value(self) -> int:
        '''
        Lets you see the highest value available for the servo

        Args:
            None

        Returns:
            int: highest value of the servo
        '''
        return self.max_value

    def get_min_value(self) -> int:
        '''
        Lets you see the lowest value available for the servo

        Args:
            None

        Returns:
            int: lowest value of the servo
        '''
        return self.min_value


    def get_pos(self) -> int:
        '''
        The position where the servo is set at the moment

        Args:
            None

        Returns:
            int: The position of the servo
        '''
        return k.get_servo_position(self.port)

    def set_pos(self, value: int, enabler_needed: bool = True) -> None:
        '''
        Sets the position of the servo

        Args:
            value (int): the value where it has to be
            enabler_needed (bool, optional): If True (default), it enables and disables the servo port. If it is set to False, then the port will not move if you did not enabled it first

        Returns:
            None
        '''
        servo_id = self._manage_servo_stopper(True)
        if self._is_servo_active(servo_id):
            self._set_pos_internal(value=value, enabler_needed=enabler_needed)
        self._manage_servo_stopper(False)

    def add_to_pos(self, value: int, enabler_needed: bool=True) -> None:
        '''
        Adds the value to the current pos

        Args:
            value (int): the value to add to the current position
            enabler_needed (bool, optional): If True (default), it enables and disables the servo port. If it is set to False, then the port will not move if you did not enabled it first

        Returns:
            None
        '''
        new_pos = self.get_pos() + value
        if self._valid_range(new_pos):
            self._set_pos_internal(new_pos, enabler_needed=enabler_needed)

    def range_to_pos(self, value:int, multi: int = 2, disabler_needed: bool= True) -> None:
        '''
        Changes the position smoothly from the current position to the position given

        Args:
            value (int): the value where it has to be at the end of the transition
            multi (int, optional): the multiplicator on how fast it should get (hint: the higher the mutli, the faster but less smooth it gets) (default: 2)
            disabler_needed (bool, optional): If True (default), it disables the servo port. If it is set to False, then the servo will not move when this function ends

        Returns:
            None
        '''
        servo_id = self._manage_servo_stopper(True)
        if multi < 1:
            multi = 1
        self._servo_enabler()
        curr_pos = self.get_pos()
        if value-curr_pos < 0:
            multi = -multi
        counter = int(multi)
        if self._valid_range(value):
            for _ in range(abs(value-curr_pos)//abs(int(multi))):
                if self._is_servo_active(servo_id):
                    self.add_to_pos(counter, enabler_needed=False)
                else:
                    break
        if disabler_needed:
            self._servo_disabler()
        self._manage_servo_stopper(False)

    def range_from_to_pos(self, interval: list, multi: int = 2, disabler_needed: bool= True) -> None:
        '''
        Changes the position smoothly from the first position in the interval to the second position in the interval

        Args:
            interval (list(int1, int2)): the values from where (int1 in the list) the servo has to go smoothly to (int2 in the list)
            multi (int, optional): the multiplicator on how fast it should get (hint: the higher the mutli, the faster but less smooth it gets) (default: 2)
            disabler_needed (bool, optional): If True (default), it disables the servo port. If it is set to False, then the servo will not move when this function ends

        Returns:
            None
        '''
        servo_id = self._manage_servo_stopper(True)
        min_val = min(int(interval[0]), int(interval[1]))
        max_val = max(int(interval[0]), int(interval[1]))
        if multi < 1:
            multi = 1

        if int(interval[0]) > int(interval[1]):
            multi = -multi

        self._servo_enabler()
        counter = int(interval[0])
        adder = int(multi)
        for _ in range((max_val-min_val)//abs(int(multi))):
            if self._is_servo_active(servo_id):
                self._set_pos_internal(counter, enabler_needed=False)
                counter += adder
            else:
                break
        if disabler_needed:
            self._servo_disabler()
        self._manage_servo_stopper(False)