#!/usr/bin/python3
import os, sys

sys.path.append("/usr/lib")

from logger import *

# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com
# Notice: feel free to write me for questions or help!
# Date of creation: 2026-03-02

try:
    import time
except Exception as e:
    log(str(e), in_exception=True)


class TimeR:
    def __init__(self):
        '''
        Class for creating consistent timer across all python files

        Args:
            None
        '''
        self.begin_time = None
        self.current_timer_type = None
        self.timer_type_secs = 'Seconds'
        self.timer_type_millis = 'Milliseconds'

    def get_current_type(self) -> str:
        '''
        Receive the current set type of the timer

        Args:
            None

        Returns:
            str: current type
        '''
        return self.current_timer_type

    def get_begin_time(self) -> float:
        '''
        Receive the time at which the timer got started

        Args:
            None

        Returns:
            float: time.time() -> returns the current time in seconds since the beginning of the epoch
        '''
        return self.begin_time


    def change_current_type(self, new_type: str):
        '''
        Change the current time convertion at which the timer currently operates

        Args:
            new_type (str): the new type (e.g.: "Seconds" or "Milliseconds")

        Returns:
            None
        '''
        if not self.current_timer_type:
            log('Timer type is not set. Please set a timer first, before changing the type!', in_exception=True)
            raise ValueError('Timer type is not set. Please set a timer first, before changing the type!')

        t = new_type.upper()
        if t == self.timer_type_secs.upper() or t == 'SECS' or t == 'SEC' or t == 'S':
            self.current_timer_type = self.timer_type_secs
        elif t == self.timer_type_millis.upper() or t == 'MILLISS' or t == 'MILLI' or t == 'MS':
            self.current_timer_type = self.timer_type_millis
        else:
            log('Timer type does not exist! Please look at the existing types!')
            raise ValueError('Timer type does not exist! Please look at the existing types!')

    def start_timer_sec(self, starting_secs=None) -> None:
        '''
        Start the timer for time examination (in seconds)

        Args:
            starting_secs (int or float): The time at which the timer should begin counting (in seconds)

        Returns:
            None
        '''
        additional_time = starting_secs if starting_secs else 0
        self.begin_time = time.time() - additional_time
        self.current_timer_type = self.timer_type_secs

    def start_timer_millis(self, starting_millis=None) -> None:
        '''
        Start the timer for time examination (in milliseconds)

        Args:
            starting_millis (int or float): The time at which the timer should begin counting (in milliseconds)

        Returns:
            None
        '''
        additional_time = starting_millis if starting_millis else 0
        self.begin_time = time.time() - additional_time/1000
        self.current_timer_type = self.timer_type_millis


    def reset_timer(self):
        '''
        Reset the current running timer to zero

        Args:
            None

        Returns:
            None
        '''
        if not self.begin_time:
            log('Timer has not been set yet')
        self.begin_time = None
        self.current_timer_type = None

    def stop_timer(self, reset_timer: bool = True) -> float:
        '''
        Stop the current running timer

        Args:
            reset_timer (bool, optional): If the timer should reset after stopping (True) or not (False) (default: True)

        Returns:
            float: The difference between the started time and the current time in the time format at which you started the timer
        '''
        if not self.begin_time or not self.current_timer_type:
            log('Timer is not set. Please set it first, before stopping it!', in_exception=True)
            raise ValueError('Timer is not set. Please set it first, before stopping it!')


        end_time = time.time()
        difference = None
        if self.current_timer_type == self.timer_type_secs:
            difference = self.begin_time - end_time

        elif self.current_timer_type == self.timer_type_millis:
            difference = (self.begin_time - end_time) * 1000

        if reset_timer:
            self.reset_timer()

        return difference

