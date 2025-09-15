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
except Exception as e:
    log(f'Import Exception in WifiConnector: {str(e)}', important=True, in_exception=True)

class ServoX:
    def __init__(self, Port: int, maxValue: int = 2047, minValue:int = 0):
        self.port = Port
        self.max_value = maxValue
        self.min_value = minValue

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
        k.disable_servo(self.port)

    def _valid_range(self, value:int) -> bool:
        '''
        Verifies, if the value is inside the min and max value of the servo

        Args:
            value (int): The number which should be checked if it is in the range

        Returns:
            bool: If it is a valid number (True), else it raises an exception
        '''
        num =  self.min_value <= value <= self.max_value
        if not num:
            log(f"{value} is out of range, where the range is between {self.min_value} to {self.max_value}", important=True, in_exception=True)
            raise Exception(f"{num} is out of range, where the range is between {self.min_value} to {self.max_value}")
        return num

    def get_pos(self) -> int:
        '''
        The position where the servo is set at the moment

        Args:
            None

        Returns:
            int: The position of the servo
        '''
        return k.get_servo_position()

    def set_pos(self, value: int, enabler_needed: bool=True) -> None:
        '''
        Sets the position of the servo

        Args:
            value (int): the value where it has to be
            enabler_needed (bool, optional): If True (default), it enables and disables the servo port. If it is set to False, then the port will not move if you did not enabled it first

        Returns:
            None
        '''
        millis = abs(self.get_pos() - value) / 10 + 10 # + 20 is just a kind of bias. @TODO -> testen, ob die formel so passt
        if enabler_needed:
            self._servo_enabler()
        if self._valid_range(value):
            k.set_servo_position(self.port, int(value))
            k.msleep(int(millis))
        if enabler_needed:
            self._servo_disabler()

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
            self.set_pos(new_pos, enabler_needed=enabler_needed)

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
        if multi < 1:
            multi = 1
        self._servo_enabler()
        curr_pos = self.get_pos()
        if value-curr_pos < 0:
            multi = -multi
        counter = int(multi)
        if self._valid_range(value):
            for _ in range(abs(value-curr_pos)//abs(int(multi))):
                self.add_to_pos(counter, enabler_needed=False)
        if disabler_needed:
            self._servo_disabler()

    def range_from_to_pos(interval: list, multi: int = 2, disabler_needed: bool= True) -> None:
        '''
        Changes the position smoothly from the first position in the interval to the second position in the interval

        Args:
            interval (list(int1, int2)): the values from where (int1 in the list) the servo has to go smoothly to (int2 in the list)
            multi (int, optional): the multiplicator on how fast it should get (hint: the higher the mutli, the faster but less smooth it gets) (default: 2)
            disabler_needed (bool, optional): If True (default), it disables the servo port. If it is set to False, then the servo will not move when this function ends

        Returns:
            None
        '''
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
            self.set_pos(counter, enabler_needed=False)
            counter += adder
        if disabler_needed:
            self._servo_disabler()