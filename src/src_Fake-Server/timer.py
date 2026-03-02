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
        self.begin_time = None
        self.current_timer_type = None
        self.timer_type_secs = 'Seconds'
        self.timer_type_millis = 'Milliseconds'



    def start_timer_sec(self):
        self.begin_time = time.time()
        self.current_timer_type = self.timer_type_secs

    def start_timer_millis(self):
        self.begin_time = time.time()
        self.current_timer_type = self.timer_type_millis

    def reset_timer(self):
        if not self.begin_time:
            log('Timer has not been set yet')
        self.begin_time = None
        self.current_timer_type = None

    def stop_timer(self, reset_timer: bool = False) -> float:
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

