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
    from servo_scheduler import SERVO_SCHEDULER  # selfmade
except Exception as e:
    log(f'Import Exception in WifiConnector: {str(e)}', important=True, in_exception=True)

class ServoX:
    def __init__(self, port: int, maxValue: int = 2047, minValue: int = 0):
        '''
        Class for using the servos. HINT: You can use this class for micro servos as well, just set the min and max values to fit the micro servo

        Args:
            port (int): The integer value from where it is plugged in (the hardware) (e.g.: 1; 3; 4; 2).
            maxValue (int, optional): The highest value which the servo can go to (default: 2047)
            minValue (int, optional): The lowest value which the servo can go to (default: 0)
        '''
        self.port = port
        self.max_value = maxValue
        self.min_value = minValue
        self._servo_lock = threading.Lock()
        self._active_servo_id = None
        self.new_pos_val = 0
        stop_manager.register_servox(self)


    # ======================== PRIVATE METHODS ========================
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
            log(f"{value} is out of range, where the range is between {self.min_value} to {self.max_value}")
            self.new_pos_val = self.min_value if value <= self.min_value else self.max_value
        return in_range

    def _set_pos_internal(self, value: int) -> None:
        '''
        Sets the position of the servo internally without a Lock, so you need to manage them

        Args:
            value (int): the value where it has to be

        Returns:
            None
        '''
        if self._valid_range(value):
            SERVO_SCHEDULER.set_position(self.port, int(value))
        else:
            SERVO_SCHEDULER.set_position(self.port, self.new_pos_val)

    def _hard_stop(self) -> None:
        SERVO_SCHEDULER.clear_list()


    # ======================== GET METHODS ========================
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


    # ======================== PUBLIC METHODS ========================
    def set_pos(self, value: int) -> None:
        '''
        Sets the position of the servo

        Args:
            value (int): the value where it has to be

        Returns:
            None
        '''
        self._set_pos_internal(value)


    def add_to_pos(self, value: int) -> None:
        '''
        Adds the value to the current pos

        Args:
            value (int): the value to add to the current position

        Returns:
            None
        '''
        new_pos = self.get_pos() + value
        if self._valid_range(new_pos):
            self._set_pos_internal(new_pos)
        else:
            self._set_pos_internal(self.new_pos_val)

    def range_to_pos(self, value: int, multi: int = 2) -> None:
        '''
        Changes the position smoothly from the current position to the position given

        Args:
            value (int): the value where it has to be at the end of the transition
            multi (int, optional): the multiplicator on how fast it should get (hint: the higher the mutli, the faster but less smooth it gets) (default: 2)

        Returns:
            None
        '''
        curr_pos = self.get_pos()

        if not self._valid_range(value):
            value = self.new_pos_val

        if multi < 1:
            multi = 1

        if abs(multi) > abs(value - curr_pos):
            multi = abs(value - curr_pos)

        if value-curr_pos < 0:
            multi = -multi


        counter = int(multi)

        if counter > 0:
            while self.get_pos() < value:
                self.add_to_pos(counter)
        else:
            while self.get_pos() > value:
                self.add_to_pos(counter)

    def range_from_to_pos(self, interval: list, multi: int = 2) -> None:
        '''
        Changes the position smoothly from the first position in the interval to the second position in the interval

        Args:
            interval (list(int1, int2)): the values from where (int1 in the list) the servo has to go smoothly to (int2 in the list)
            multi (int, optional): the multiplicator on how fast it should get (hint: the higher the mutli, the faster but less smooth it gets) (default: 2)

        Returns:
            None
        '''
        for i in range(len(interval)):
            interval[i] = int(interval[i]) if self._valid_range(interval[i]) else self.new_pos_val

        self.set_pos(interval[0])
        self.range_to_pos(interval[1], multi)