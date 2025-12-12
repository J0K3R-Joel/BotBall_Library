#!/usr/bin/python3
import os, sys

sys.path.append("/usr/lib")

from logger import *

# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com
# Notice: feel free to write me for questions or help!
# Date of creation: 2025-11-24

try:
    import _kipr as k
    import time
    import threading
    import inspect
    import hashlib
    import random
    from collections import defaultdict
    from fileR import FileR  # selfmade
    from motor_scheduler import MOTOR_SCHEDULER  # selfmade
    from stop_manager import stop_manager  # selfmade
except Exception as e:
    log(f'Import Exception: {str(e)}', important=True, in_exception=True)

_GLOBAL_MAIN_ID = None

class WheelR:

    def __init__(self, Port: int, max_speed: int = 1500, default_speed: int = 1400, servo_like: bool = False):  # @TODO -> servo like motor
        self.port = Port
        self.max_speed = max_speed
        self.d_speed = default_speed
        stop_manager.register_wheelr(self)

    # ======================== PRIVATE METHODS ========================

    def _base_speed_func(self, speed: int) -> None:
        '''
        Function where you can tell the robot the base function of how to drive / with which function and functionality it should drive

        Args:
            speed (int): The velocity the robot should go. currently with the mav function (values range: -1500 to 1500)

        Returns:
            None
        '''
        if speed < -self.max_speed:
            speed = -self.max_speed
        elif speed > self.max_speed:
            speed = self.max_speed

        MOTOR_SCHEDULER.set_speed(self.port, speed)


    def _hard_stop(self) -> None:
        MOTOR_SCHEDULER.clear_list()
    # ======================== GET METHODS ========================

    def get_port(self) -> int:
        '''
        Lets you see the port which this instance is assigned to

        Returns:
            int: port number of the motor
        '''
        return self.port

    def get_max_speed(self) -> int:
        '''
        Lets you see the current max speed

        Returns:
            int: maximum speed you are able to drive
        '''
        return self.max_speed

    def get_default_speed(self) -> int:
        '''
        Lets you see the default speed

        Returns:
            int: default speed you are able to drive
        '''
        return self.d_speed

    def get_speed(self) -> int:
        '''
        Lets you see the default speed

        Returns:
            int: default speed you are able to drive
        '''
        return self.get_default_speed()

    # ======================== SET METHODS ========================
    def set_port(self, port_number: int) -> None:
        '''
        Assign the instance to a new port

        Args:
            port_number (int): new port from the motor
        '''
        self.port = port_number

    def set_max_speed(self, max_speed: int) -> None:
        '''
        Change the max speed to a new max speed

        Args:
            max_speed (int): new max speed that you can't exceed

        Returns:
            None
        '''
        self.max_speed = max_speed

    def set_default_speed(self, default_speed: int) -> None:
        '''
        Change the default speed to a new default speed

        Args:
            default_speed (int): new default speed

        Returns:
            None
        '''
        self.d_speed = default_speed


    # ======================== PUBLIC METHODS =======================
    def test_plugged_in(self) -> None:
        '''
        Lets you test, if the motor is plugged in (will not test the correct direction!)

        Returns:
            None, but either throws an exception (if not plugged in) or prints a success message
        '''
        k.cmpc(self.port)
        begin_counter = k.gmpc(self.port)
        self.drive_time(100, 100)

        if k.gpmc(self.port) - begin_counter == 0:
            log(f'Motor on port {self.port} is not plugged in!', in_exception=True)
            raise Exception(f'Motor on port {self.port} is not plugged in!')

        print(f'Success! Motor {self.port} plugged in.', flush=True)


    def fw(self, speed: int) -> None:
        '''
        Function for driving forward (expects that the motor will move forwards when the value gets positive)

        Args:
            speed (int): velocity to drive forward

        Returns:
            None
        '''
        if speed < 0:
            speed = -speed

        self._base_speed_func(speed)
    def forward(self, speed: int) -> None:
        '''
        Function for driving forward (expects that the motor will move forwards when the value gets positive)

        Args:
            speed (int): velocity to drive forward

        Returns:
            None
        '''
        self.fw(speed)

    def forward_default(self) -> None:
        '''
        Function for driving forward with default speed (expects that the motor will move forwards when the value gets positive)

        Args:
            None

        Returns:
            None
        '''
        self.fw(self.d_speed)

    def forward_max(self):
        '''
        Function for driving forward with maximum speed (expects that the motor will move forwards when the value gets positive)

        Args:
            None

        Returns:
            None
        '''
        self.fw(self.max_speed)


    def bw(self, speed: int) -> None:
        '''
        Function for driving backwards (expects that the motor will move backwards when the value gets negative)

        Args:
            speed (int): velocity to drive forward

        Returns:
            None
        '''
        if speed > 0:
            speed = -speed
        self._base_speed_func(speed)
    def backward(self, speed: int) -> None:
        '''
        Function for driving backwards (expects that the motor will move backwards when the value gets negative)

        Args:
            speed (int): velocity to drive forward

        Returns:
            None
        '''
        self.bw(-speed)

    def backward_default(self) -> None:
        '''
        Function for driving backwards with default speed (expects that the motor will move backwards when the value gets negative)

        Args:
            None

        Returns:
            None
        '''
        self.bw(-self.d_speed)

    def backward_max(self) -> None:
        '''
        Function for driving backwards with maximum speed (expects that the motor will move backwards when the value gets negative)

        Args:
            None

        Returns:
            None
        '''
        self.bw(-self.max_speed)


    def drive(self, speed:int):
        '''
        Default Function for driving in any direction

        Args:
            speed (int): velocity to drive

        Returns:
            None
        '''
        self._base_speed_func(speed)

    def drive_dfw(self, adjuster: int = None) -> None:
        '''
        Function for driving forward with default speed (expects that the motor will move forwards when the value gets positive)

        Args:
            adjuster (int, optional): velocity of change absolute to the default speed (default: None) (eg: adjuster=200, then speed = default_speed + 200)

        Returns:
            None
        '''
        if isinstance(adjuster, float):
            adjuster = int(adjuster)
        elif not isinstance(adjuster, int):
            adjuster = 0

        self.drive(self.d_speed + adjuster)

    def drive_dbw(self, adjuster: int = None) -> None:
        '''
        Function for driving backward with default speed (expects that the motor will move backwards when the value gets negative)

        Args:
            adjuster (int, optional): velocity of change absolute to the default speed (default: None) (eg: adjuster=200, then speed = - default_speed + 200)

        Returns:
            None
        '''
        if isinstance(adjuster, float):
            adjuster = int(adjuster)
        elif not isinstance(adjuster, int):
            adjuster = 0

        self.drive(-self.d_speed + adjuster)

    def drive_mfw(self, adjuster: int = None) -> None:
        '''
        Function for driving forward with maximum speed (expects that the motor will move forwards when the value gets positive)

        Args:
            adjuster (int, optional): velocity of change absolute to the maximum speed (default: None) (eg: adjuster=-200, then speed = maximum_speed - 200)

        Returns:
            None
        '''
        if isinstance(adjuster, float):
            adjuster = int(adjuster)
        elif not isinstance(adjuster, int):
            adjuster = 0

        if adjuster < 0:
            adjuster = -adjuster

        self.drive(self.max_speed - adjuster)

    def drive_mbw(self, adjuster: int = None) -> None:
        '''
        Function for driving backward with maximum speed (expects that the motor will move backwards when the value gets nedative)

        Args:
            adjuster (int, optional): velocity of change absolute to the maximum speed (default: None) (eg: adjuster=200, then speed = -maximum_speed + 200)

        Returns:
            None
        '''
        if isinstance(adjuster, float):
            adjuster = int(adjuster)
        elif not isinstance(adjuster, int):
            adjuster = 0

        if adjuster < 0:
            adjuster = -adjuster

        self.drive(-self.max_speed + adjuster)


    def drive_time(self, speed: int, millis: int) -> None:
        '''
        Default Function for driving in any direction for a time

        Args:
            speed (int): velocity to drive
            millis (int): time (in milliseconds) on how long it should drive

        Returns:
            None
        '''
        start_time = k.seconds()
        while k.seconds() - start_time < millis/1000:
            self.drive(speed)