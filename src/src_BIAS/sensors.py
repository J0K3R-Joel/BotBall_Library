import os, sys
sys.path.append("/usr/lib")

from logger import *  # selfmade

# Author: Joel Kalkusch
# Email: kalkusch.joel@gmail.com
# Notice: feel free to write me for questions or help!
# Date of creation: 2026-02-10

try:
    import _kipr as k
    from abc import ABC, abstractmethod
except Exception as e:
    log(f'Import Exception: {str(e)}', important=True, in_exception=True)

class Sensor(ABC):

    @abstractmethod
    def current_value(self):
        '''
        get the current value of the sensor

        Args:
            None

       Returns:
            value of the sensor
        '''
        return