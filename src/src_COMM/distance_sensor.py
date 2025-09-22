#!/usr/bin/python3
import os, sys
sys.path.append("/usr/lib")

from logger import *

# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com
# Notice: feel free to write me for questions or help!
# Date of creation: 2025-07-28

try:
    import _kipr as k
    import time
except Exception as e:
    log(f'Import Exception: {str(e)}', important=True, in_exception=True)


class DistanceSensor:
    def __init__(self, Port):
        self.port = Port


    # ======================== PUBLIC METHODS ========================

    def current_value(self) -> int:
        '''
        get the current value of the distance sensor

        Args:
            None

       Returns:
            current value of the assigned analog Port of the distance sensor (int)
        '''
        return k.analog(self.port)
