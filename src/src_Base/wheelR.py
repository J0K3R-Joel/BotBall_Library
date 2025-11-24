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
except Exception as e:
    log(f'Import Exception: {str(e)}', important=True, in_exception=True)

class WheelR:
    def __init__(self, Port: int, max_speed: int = 1500, default_speed: int = 1400, servo_like: bool = False):  # @TODO -> servo like motor
        self.port = Port
        self.max_speed = max_speed
        self.d_speed = default_speed

    def __getattr__(self, name):
        if hasattr(k, name):
            attr = getattr(k, name)
            if callable(attr):
                def wrapper(*args, **kwargs):
                    return attr(*args, **kwargs)
                return wrapper
            return attr
        log(f'"{type(self).__name__}" object has no attribute "{name}"', in_exception=True)
        raise AttributeError(f'"{type(self).__name__}" object has no attribute "{name}"')


    def get_port(self):
        return self.port

    def get_max_speed(self):
        return self.max_speed

    def get_default_speed(self):
        return self.d_speed

    def get_speed(self):
        return self.get_default_speed()


    def set_max_speed(self, max_speed: int):
        self.max_speed = max_speed

    def set_default_speed(self, default_speed: int):
        self.d_speed = default_speed



    def fw(self, speed: int):
        k.mav(self.port, abs(speed))
    def forward(self, speed: int):
        self.fw(speed)

    def forward_default(self):
        self.fw(self.d_speed)

    def forward_max(self):
        self.fw(self.max_speed)



    def bw(self, speed: int):
        k.mav(self.port, -abs(speed))
    def backward(self, speed: int):
        self.bw(-speed)

    def backward_default(self):
        self.bw(-self.d_speed)

    def backward_max(self):
        self.bw(-self.max_speed)


    def drive(self, speed:int):
        k.mav(self.port, speed)

    def drive_dfw(self, adjuster: int = None):
        if isinstance(adjuster, float):
            adjuster = int(adjuster)
        elif not isinstance(adjuster, int):
            adjuster = 0
        self.drive(self.d_speed + adjuster)

    def drive_dbw(self, adjuster: int = None):
        if isinstance(adjuster, float):
            adjuster = int(adjuster)
        elif not isinstance(adjuster, int):
            adjuster = 0
        self.drive(-self.d_speed + adjuster)

    def drive_mfw(self, adjuster: int = None):
        if isinstance(adjuster, float):
            adjuster = int(adjuster)
        elif not isinstance(adjuster, int):
            adjuster = 0
        self.drive(self.max_speed - abs(adjuster))

    def drive_mbw(self, adjuster: int = None):
        if isinstance(adjuster, float):
            adjuster = int(adjuster)
        elif not isinstance(adjuster, int):
            adjuster = 0
        self.drive(-self.max_speed + abs(adjuster))


    def drive_time(self, speed: int, millis: int):
        start_time = k.seconds()
        while k.seconds() - start_time < millis/1000:
            self.drive(speed)

    def stop(self):
        k.freeze(self.port)




