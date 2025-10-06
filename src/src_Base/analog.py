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
    def __init__(self, Port):
        self.port = Port

    def current_value(self):
        '''
        get the current value of the distance sensor

        Args:
            None

       Returns:
            current value of the assigned analog Port of the distance sensor (int)
        '''
        return k.analog(self.port)