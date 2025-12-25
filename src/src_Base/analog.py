import os, sys
sys.path.append("/usr/lib")

from logger import *  # selfmade

# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com
# Notice: feel free to write me for questions or help!
# Date of creation: 2025-10-06

try:
    import _kipr as k
except Exception as e:
    log(f'Import Exception: {str(e)}', important=True, in_exception=True)

class Analog:
    def __init__(self, port: int):
        '''
        Class for every analog sensor available

        Args:
            port (int): The integer value from where it is plugged in (the hardware) e.g.: 1; 3; 4; 2.
        '''
        self.port = port

    def current_value(self) -> int:
        '''
        get the current value of the distance sensor

        Args:
            None

       Returns:
            int: current value of the assigned analog Port of the distance sensor (int)
        '''
        return k.analog(self.port)